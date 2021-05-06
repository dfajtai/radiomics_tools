#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Short explanation"""

import sys
import nibabel as nib
from nibabel.spatialimages import SpatialImage
import math
from scipy.ndimage.filters import gaussian_filter, median_filter
from types import *
import copy
from skimage.morphology import reconstruction
import SimpleITK as sitk
from scipy.ndimage.measurements import center_of_mass

from nibabel.processing import resample_from_to
import nibabel.processing

NoneType = type(None)

import scipy.ndimage as ndimage

sys.path.insert(0, '/home/fajtai/py/')

from Std_Tools.common.command_runner.command_runner import CommandRunner
from Common.colorPrint import *
from Std_Tools.img_proc.IO.affine_handler import *
from Std_Tools.img_proc.labeling import labelData
from Std_Tools.img_proc.bounding_box_functions import bbox_3d_with_iso_border

from Std_Tools._template_paths_ import T1_2mm
from Std_Tools.visualization.fast_plots import fast_hist

class NibImg(object):
    def __init__(self,img=None, dtype = "float32", reorient = False, img_path = None, negative_step_correction = False, *args, **kwargs):
        self._img = img
        self.step_sizes = None

        self._data = None
        self._affine = None

        self.dtype = dtype

        self.img_path = img_path
        self.intensity_scaling_factor = 1


        if isinstance(img,NibImg):
            self._img = img.img
            self.step_sizes = img.step_sizes
            self._data = img.data
            self._affine = img.affine
            self.dtype = img.dtype
            self.img_path = img.img_path
            self.intensity_scaling_factor = img.intensity_scaling_factor
        else:
            self._init_from_img(img,reorient = reorient, negative_step_correction=negative_step_correction)

    @staticmethod
    def try_img(img):
        try:
            I = read_image(img)
            if not isinstance(I,NibImg):
                return False
            else:
                img = I
                return img
        except Exception as e:
            print(e.message)
            raise e

    #basic informations

    def _init_from_img(self,img,reorient = False, negative_step_correction = False):
        if isinstance(img,SpatialImage):
            if reorient:
                orient = list(nib.aff2axcodes(img.affine))
                if orient != ["R", "A", "S"]:
                    img = nib.as_closest_canonical(img)


            self._img = img

            self._affine= self._img.affine

            self.step_sizes = img.header.get_zooms()

            self._data = self.get_data()

            if negative_step_correction and self.has_neagtive_step():
                #todo negative step correction
                self.n_step_correction()



    def has_neagtive_step(self):
        diagonal = np.array(self.affine).diagonal()
        if any([d<0 for d in diagonal]):
            return True

    def n_step_correction(self):
        print("negative step correction")
        diagonal = np.array(self.affine).diagonal()
        for axis in range(len(diagonal)):
            if diagonal[axis]<0:
                #flip data
                self.data = np.flip(self.data,axis)
                #fix origin
                self.affine[axis, -1] = self.affine[axis, -1] + (np.shape(self.data)[axis] - 1 )* self.affine[axis, axis]
                #fix step size
                self.affine[axis,axis] = self.affine[axis,axis]*-1




    def get_data(self):
        return self._img.get_data().astype(self.dtype)

    @property
    def TR(self):
        if len(self.step_sizes)<4:
            return
        else:
            return self.step_sizes[3]

    @property
    def shape(self):
        return self._data.shape

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = copy.copy(new_data)

    @property
    def affine(self):
        return self._affine

    @affine.setter
    def affine(self, new_affine):
        self._affine = copy.copy(new_affine)

    @property
    def affine_origin(self):
        if isinstance(self.affine,np.ndarray):
            return self._affine[0:3,3]

    @affine_origin.setter
    def affine_origin(self,new_origin):
        n = new_origin[:]
        for i in range(3):
            self._affine[i,3] = n[i]

    def real_step_sizes(self):
        affine = self._affine[0:3, 0:3]

        def correctSizes(affine):
            signs = np.sign(affine)  # előjelek...
            signs = np.array([signs[:, i][signs[:, i] != 0] for i in [0, 1, 2]])  # 0 előjel figyelmen kívül hagyása
            signs = np.array([np.prod(signs[i]) for i in [0, 1, 2]])  # előjelek szorzata...
            return signs

        sizes = [np.linalg.norm(affine[i, :]) for i in [0, 1, 2]]
        sizes = sizes * correctSizes(affine)

        return sizes

    @property
    def vox_vol(self):
        sizes = self.real_step_sizes()
        return abs(np.product(sizes))

    def extract_img(self):
        _data = self.data.astype(self.dtype)
        newImg = nib.Nifti1Image(_data, self.affine)

        return newImg

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, value):
        self._init_from_img(value)

    def c(self):
        I = copy.deepcopy(self)
        I.data = np.copy(self.data)
        I._img = copy.copy(self._img)
        I._affine = copy.copy(self._affine)
        return I

    #file io

    def save(self,save_path,data = None,affine = None,header = None,dtype = "float32", gz = False, RAS = False):
        if not CommandRunner.runSwitch:
            printExtra("Saving {0}".format(save_path))
            return

        D = data if not isinstance(data,NoneType) else self.data
        A = affine if not isinstance(affine,NoneType) else self.affine

        if gz and not str(save_path).endswith(".gz"):
            save_path = "{0}.gz".format(str(save_path))

        self.img_path  = save_path

        save_image(str(save_path),D,A,header,dtype, RAS  = RAS)


    def safe_save(self,save_path,affine = None,header = None,dtype = "float32"):
        if CommandRunner.runSwitch:
            if not os.path.exists(str(save_path)) or CommandRunner.overwrite:
                self.save(save_path=save_path,affine=affine,header=header,dtype=dtype)

    #world functions
    def voxel_2_world(self,voxel_coord,ignore_negative_step = False):
        return voxel_2_world(voxel_coord,self.affine,ignore_negative_step=ignore_negative_step)


    def world_2_voxel(self,world_coord,toIndex = True, ignore_negative_step = False, abs_negative_voxel_coord=True):
        return world_2_voxel(world_coord,self.affine,
                             toIndex=toIndex,ignore_negative_step=ignore_negative_step,
                             abs_negative_voxel_coord=abs_negative_voxel_coord)




    #basic transformation, operation
    def factor_scaling(self, scaling_factor, indices= None, inplace = True):
        _data = copy.copy(self.data)
        if isinstance(indices,np.ndarray):
            if indices.shape != self.data.shape:
                return
            scaling_matrix = np.ones_like(indices)
            scaling_matrix[indices==1] = scaling_factor
            _data = _data*scaling_matrix
        else:
            _data = _data*scaling_factor
        self.intensity_scaling_factor = scaling_factor

        if not inplace:
            return NibImg(nib.Nifti1Image(_data, self.affine))
        self._data = _data
        return self

    def translation(self,translation_vector, inplace = True):
        a = copy.copy(self.affine_origin)
        a = np.array(a)+np.array(translation_vector)

        if not inplace:
            return NibImg(nib.Nifti1Image(self._data, a))
        self._affine = a
        return self

    def mirror(self,mirroring_vector, inplace = True):
        _data = copy.copy(self.data)
        for i in zip(_data.shape,range(len(mirroring_vector))):
            if mirroring_vector[i[1]] == -1:
                _data = np.flip(_data,i[1])

        if not inplace:
            return NibImg(nib.Nifti1Image(_data, self.affine))
        self._data = _data
        return self

    #basic image processing

    @property
    def center_of_gravity(self):
        return center_of_mass(self.data)

    def apply_mask(self, *masks):
        for m in masks:
            if isinstance(m,np.ndarray):
                if self.data.shape == m.shape:
                    self.data = self.data * m
                continue

            if isinstance(m, SpatialImage):
                m = NibImg(m)

            if isinstance(m, NibImg):
                self.data = self.data*m.data

        return self

    def to_bin(self,low=0.0, high = None, inplace = True):
        if not high:
            high = np.max(self.data)

        binary_img = np.zeros_like(self.data)
        binary_img[np.logical_and(self.data>low, self.data<=high)]=1

        if inplace:
            self.data = binary_img
            return self
        else:
            return NibImg(nib.Nifti1Image(binary_img, self.affine))


    def threshold(self,low=0, high = None, low_value = 0, high_value = 0, inplace = True):
        D = copy.copy(self.data)
        if not high:
            high = np.max(D)
        if not low:
            low = np.min(D)

        D[D<low] = low_value
        D[D>high] = high_value

        if inplace:
            self.data = D
            return self

        I = self.c()
        I.data = D
        return I

    def otsu_simple_thr(self,levels = 128, low_val = 0, classes = 1, inplace = False):
        I = sitk.GetImageFromArray(self.data)
        I = sitk.OtsuMultipleThresholds(I, classes, 0, levels)
        M = sitk.GetArrayFromImage(I)

        T = np.max(self.data[M==0])
        print("The Otsu based threshold value is {0}".format(str(T)))

        if inplace:
            self.data[M==0] = low_val
            return self

        I = self.c()
        I.data[M==0] = low_val
        return I

    def median_filter(self, size, inplace = True):
        __data = median_filter(self.data,size = size)

        if not inplace:
            return NibImg(nib.Nifti1Image(__data, self.affine))
        self._data = __data
        return self

    def smooth(self,fwhm, inplace = True):
        def fwhm_2_sigma(fwhm):
            sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
            return sigma

        if not isinstance(fwhm,list):
            _fwhm =[]
            _fwhm +=[fwhm]*3
            fwhm = _fwhm[:]

        if isinstance(fwhm,list):
            if len(fwhm)< len(self.data.shape):
                fwhm += [0]*(len(self.data.shape)-len(fwhm))

        for i in range(3):
            fwhm[i] = fwhm[i]/self.step_sizes[i]

        if any([f>0.0 for f in fwhm]):

            sigma = [fwhm_2_sigma(f) for f in fwhm]

            data = gaussian_filter(self.data.astype("float32"),sigma,0).astype("float32")

            if not inplace:
                return NibImg(nib.Nifti1Image(data, self.affine))
            self._data = data
            return self

        if not inplace:
            return self.data
        else:
            return self

    def gradient(self, inplace = True):
        grad_data = np.gradient(self._data)
        norm_grad_data = np.linalg.norm(grad_data, axis=0)

        if not inplace:
            return NibImg(nib.Nifti1Image(norm_grad_data, self.affine))
        self._data = norm_grad_data
        return self

    def label(self, inplace=False, highpass=0, keep_n_largest=None, struct=None, min_size = 1):
        data = (self.data>highpass).astype("int")

        _labeled_data,label_count = labelData(data,struct=struct)

        unique, counts = np.unique(_labeled_data, return_counts=True)
        counts = zip(unique, counts)
        counts = sorted(counts, key=lambda x: x[1], reverse=True)

        labeled_data = np.zeros_like(_labeled_data)

        if isinstance(keep_n_largest, type(None)) or (not keep_n_largest):
            for i in range(1, len(counts)):
                if counts[i][1]>min_size:
                    labeled_data[_labeled_data == counts[i][0]] = i
                else:
                    break

        else:
            keep_n_largest = int(keep_n_largest)
            for i in range(1, min(len(counts), keep_n_largest)+1):
                if counts[i][1] > min_size:
                    labeled_data[_labeled_data == counts[i][0]] = i
                else:
                    break

        if inplace:
            self.data = labeled_data
            return self

        else:
            return NibImg(nib.Nifti1Image(labeled_data, self.affine))

    def lin_normalize(self,output_range =None, inplace= True):
        """
        Simple linear intensity normalization\n
        :param output_range: list, [out_min,out_max]. Default: [0.0,1.0]
        :return: self
        """
        if isinstance(output_range,NoneType):
            output_range= [0.0,1.0]
        elif hasattr(output_range,"__iter__"):
            output_range=list(output_range[:2])

        normalized = np.interp(self.data,(np.min(self.data),np.max(self.data)),tuple(output_range))
        if inplace:
            self.data = normalized
            return self
        else:
            return normalized

    def resample_like(self, img_like, interp = 1, inplace = True):
        """
        :param img_like: 'like' nib image or image path
        :param interp: 1 - trilinear, 3 - spline
        :param inplace: inplace or not
        :return: resampled nib image
        """
        if isinstance(img_like, str):
            img_like = read_image(img_like)
        if not isinstance(img_like, NibImg):
            return

        resampled = NibImg(resample_from_to(self.img,img_like.img, order = interp))

        if inplace:
            # self._img = NibImg(resampled._img)
            # self._data = self._img.data
            self._init_from_img(resampled.img)
        else:
            return resampled

    def apply_img_affine(self,spline_order = 3, constant_value = 0, inplace = True):
        fixed = nib.processing.resample_to_output(self.img,self.step_sizes, mode='constant',cval= constant_value, order=spline_order)
        if inplace:
            self.img = fixed
        else:
            return NibImg(fixed,img_path=self.img_path)

    def dilate(self,N = 1, kernel = None, inplace = True):
        data = ndimage.binary_dilation(self.data, structure=kernel, iterations=N).astype('int')
        if inplace:
            self.data=data
            return self
        return NibImg(nib.Nifti1Image(data, self.affine))

    def erode(self,N=1,kernel = None, inplace = True):

        data = ndimage.binary_erosion(self.data, structure=kernel, iterations=N).astype('int')
        if inplace:
            self.data=data
            return self
        return NibImg(nib.Nifti1Image(data, self.affine))


    def close(self,N = 1,kernel = None, inplace = True):
        data = ndimage.binary_closing(self.data, structure=kernel, iterations=N).astype('int')
        if inplace:
            self.data=data
            return self
        return NibImg(nib.Nifti1Image(data, self.affine))


    def open(self,N = 1,kernel = None, inplace = True):
        data = ndimage.binary_opening(self.data, structure=kernel, iterations=N).astype('int')
        if inplace:
            self.data=data
            return self
        return NibImg(nib.Nifti1Image(data, self.affine))

    def morph_clean_with_recon(self,kernel = None, erosion_count = 1,inplace = True):
        if erosion_count<1:
            return self

        seed = ndimage.binary_erosion(self.data, structure=kernel, iterations=erosion_count).astype('int')
        data = reconstruction(seed,self.data)

        if inplace:
            self.data = data
            return self
        return NibImg(nib.Nifti1Image(data, self.affine))

    def fill_holes(self, kernel = None, inplace = True):
        data = np.zeros_like(self.data)
        ndimage.binary_fill_holes(self.data,output=data, structure= kernel)
        if inplace:
            self.data = data
            return self
        return NibImg(nib.Nifti1Image(data, self.affine))

    def fill_holes_with_labeling(self, main_object_count = 1, inplace = True):
        data = np.logical_not(self.data==1)

        labeledData, numOfLabels = labelData(data)
        values, counts = np.unique(labeledData, return_counts=True)
        counts = zip(values, counts)
        counts = sorted(counts, key=lambda x: x[1], reverse=True)

        _data = np.zeros_like(data)

        #the first main_object_count+1 element is the background and the main object

        for i in range(main_object_count+1,numOfLabels):
            _data[labeledData==counts[i][0]] = 1

        data = np.logical_or(_data,self.data)

        if inplace:
            self.data = data
            return self
        return NibImg(nib.Nifti1Image(data, self.affine))

    def contour(self,offset=1, inset=0,contour_val = 1,kernel = None, inplace=False):
        dilated = copy.copy(self.data)
        if offset > 0:
            dilated = ndimage.binary_dilation(dilated, structure=kernel, iterations=offset).astype('int')

        eroded = copy.copy(self.data)
        if inset > 0:
            eroded = ndimage.binary_erosion(eroded, structure=kernel, iterations=inset).astype('int')

        contour = np.zeros_like(dilated)
        contour[dilated>0]=contour_val
        contour[eroded>0]=0

        if not inplace:
            return NibImg(nib.Nifti1Image(contour.astype(int), self.affine))
        self._data = contour
        return self

    def mask_scaling(self, binary_mask, target_mean = 50.0, inplace = True):
        if not isinstance(binary_mask, np.ndarray):
            return
        if binary_mask.shape != self.data.shape:
            return
        print("Number of voxels in mask: {0}".format(str(np.sum(binary_mask))))
        actual_mean = np.mean(self._data[binary_mask.astype("bool")])
        print("Actual mean of masked indices: {0}".format(str(actual_mean)))
        mask_scaling_factor = target_mean/actual_mean
        print("Scaling factor {0}".format(str(mask_scaling_factor)))
        return self.factor_scaling(mask_scaling_factor,inplace=inplace)

    def convert_labels_to_mask(self,label_list,inplace=True):
        new_data = np.zeros_like(self.data)
        for l in label_list:
            new_data[self.data==l]=1
        if inplace:
            self.data= new_data
            return self
        else:
            return NibImg(nib.Nifti1Image(new_data, self.affine))


    def get_bounding_box(self, border = 0, thr = None, otsu_thr = False):
        I = self.c()

        if type(thr) != type(None):
            I.threshold(low=thr,inplace=True)

        if otsu_thr:
            I.otsu_simple_thr(inplace=True)

        data = I.data

        p1,p2 = bbox_3d_with_iso_border(data,border=border)

        return p1,p2

    def box_crop_world(self,p1w,p2w, target_origin=None, inplace = True):
        p1 = self.world_2_voxel(p1w,ignore_negative_step=False,abs_negative_voxel_coord=False)
        p2 = self.world_2_voxel(p2w,ignore_negative_step=False,abs_negative_voxel_coord=False)

        p1c = correct_vox_coord(p1, self.shape)
        p2c = correct_vox_coord(p2, self.shape)

        x_lim = sorted([p1c[0],p2c[0]])
        y_lim = sorted([p1c[1],p2c[1]])
        z_lim = sorted([p1c[2],p2c[2]])

        data = self.data[x_lim[0]:x_lim[1], y_lim[0]:y_lim[1], z_lim[0]:z_lim[1]]

        if target_origin == None:
            target_origin = p1w

        corrected_origin = target_origin

        if isinstance(target_origin,list) or isinstance(target_origin,tuple):
            p1w_c = self.voxel_2_world(p1, ignore_negative_step=True)
            conversion_displace = np.array(p1w_c) - np.array(p1w)

            correction_displace = np.array(p1c)-np.array(p1)
            ss = np.array(get_step_sizes(self.affine,correct_negative_step=True))
            displacement = conversion_displace +(correction_displace*ss)
            corrected_origin = np.array(target_origin)+ displacement

        if inplace:
            self.data = data
            self.affine_origin = corrected_origin
            return self
        else:
            I = NibImg(nib.Nifti1Image(data, self.affine))
            I.affine_origin = corrected_origin
            return I

    def box_crop_world_rel(self,p1w,vox_count, target_origin=None, inplace = True):
        p1 = self.world_2_voxel(p1w, ignore_negative_step=True, abs_negative_voxel_coord=False)
        p2 = tuple(np.array(p1) + np.array(vox_count))

        p1c = correct_vox_coord(p1, self.shape)
        p2c = correct_vox_coord(p2, self.shape)

        data = self.data[p1c[0]:p2c[0], p1c[1]:p2c[1], p1c[2]:p2c[2]]

        if target_origin == None:
            target_origin = p1w

        corrected_origin = target_origin

        if isinstance(target_origin,list) or isinstance(target_origin,tuple):
            p1w_c = self.voxel_2_world(p1, ignore_negative_step=True)
            conversion_displace = np.array(p1w_c) - np.array(p1w)

            correction_displace = np.array(p1c)-np.array(p1)
            ss = np.array(get_step_sizes(self.affine,correct_negative_step=True))
            displacement = conversion_displace +(correction_displace*ss)
            corrected_origin = np.array(target_origin)+ displacement

        if inplace:
            self.data = data
            self.affine_origin = corrected_origin
            return self
        else:
            I = NibImg(nib.Nifti1Image(data, self.affine))
            I.affine_origin = corrected_origin
            return I


    def box_crop_voxel(self,p1,p2, inplace = True):
        p1w = self.voxel_2_world(p1, ignore_negative_step=True)
        data = self.data[p1[0]:p2[0], p1[1]:p2[1], p1[2]:p2[2]]
        affine_origin = p1w

        if inplace:
            self.data = data
            self.affine_origin = affine_origin
            return self
        else:
            I = NibImg(nib.Nifti1Image(data, self.affine))
            I.affine_origin = affine_origin
            return I

    def padding_to_cubic_size(self, target_size = 256, mask = None, box_threshold = None, otsu_thr = False, background_value=0, inplace = True):
        I = self.c()

        if len(I.shape)>3:
            #method only implemented for 3d images
            raise NotImplementedError

        # fast_hist(I.data,log_scale=True)

        if isinstance(mask,NibImg):
            p1,p2 = mask.get_bounding_box(border=0,thr = 0, otsu_thr = otsu_thr)
        else:
            if isinstance(mask,np.ndarray):
                I.data = I.data*mask
            p1,p2 = I.get_bounding_box(border=0,thr = box_threshold, otsu_thr = otsu_thr)


        I.box_crop_voxel(p1,p2,inplace=True)

        # fast_hist(I.data, log_scale=True)

        sizes = I.shape

        if not all([s<=target_size for s in sizes]):
            #find closest cubic size
            for _s in np.power(2,range(10)):
                if all([s<=_s for s in sizes]):
                    target_size = _s
                    break

        #determine start index
        sp=[] #start position
        for i in range(len(sizes)):
            sp.append(int((np.floor_divide(target_size,2.0))-np.ceil(sizes[i]/2.0)))

        #calculate new origin from start index
        padding_displacement = np.array(I.step_sizes)*np.array(sp)
        I.affine_origin = np.array(I.affine_origin)-padding_displacement

        padded_data = (np.ones([target_size] * 3) * background_value).astype(self.data.dtype)
        padded_data[sp[0]:sp[0]+sizes[0],sp[1]:sp[1]+sizes[1],sp[2]:sp[2]+sizes[2]] = self.data[p1[0]:p2[0],p1[1]:p2[1],p1[2]:p2[2]]

        if inplace:
            self.data = padded_data
            self.affine_origin = I.affine_origin
            return self
        else:
            I.data = padded_data
            return I


    def to_zero(self):
        self.data = np.zeros_like(self.data)
        return self

    def to_one(self):
        self.data = np.zeros_like(self.data)
        return self

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index,value):
        self.data[index] = value

    def __eq__(self, other):
        return self.data == other

    def __gt__(self, other):
        return self.data > other

    def __lt__(self, other):
        return self.data < other

    def __le__(self, other):
        return self.data <= other

    def __ge__(self, other):
        return self.data >= other

    def __ne__(self, other):
        return self.data != other


def read_image(image_path,dtype='float32',reorient = False,negative_step_correction = False):
    if isinstance(image_path,NibImg):
        return image_path

    image_path = str(image_path)
    if os.path.exists(image_path):
        img = nib.load(image_path)

        if reorient:
            orient = list(nib.aff2axcodes(img.affine))
            if orient != ["R", "A", "S"]:
                img = nib.as_closest_canonical(img)
        return NibImg(img, dtype=dtype, reorient=reorient, img_path= image_path, negative_step_correction = negative_step_correction)
    else:
        printError("Error during opening image '{0}': image file not exists!".format(image_path))

def save_image(save_path,data, affine,header = None, dtype = "float32", RAS = True):
        _data = data.astype(dtype)

        newImg = nib.Nifti1Image(_data, affine)
        if header != None:
            for k in newImg.header.keys():
                newImg.header[k] = header[k]

        if CommandRunner.runSwitch == True:
            printInfo("Saving {0}".format(save_path))

            if RAS:
                orig_orient = nib.orientations.aff2axcodes(newImg.affine)
                if orig_orient != ("R","A","S"):
                    print("original orientation: {0}".format(str(orig_orient)))
                    if orig_orient[0]!="R":
                        newImg = newImg.slicer[::-1,:,:]
                    if orig_orient[1]!="A":
                        newImg = newImg.slicer[:,::-1,:]
                    if orig_orient[2]!="S":
                        newImg = newImg.slicer[:, :, ::-1]
                    print("new orientation: {0}".format(str(nib.orientations.aff2axcodes(newImg.affine))))
            nib.save(newImg, save_path)
        else:
            printExtra("Saving {0}".format(save_path))


def main():
    pass


if __name__ == '__main__':
    main()
