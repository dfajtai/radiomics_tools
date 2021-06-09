import copy

import numpy as np
import pydicom as dicom
import sys, os, glob
import math
NoneType = type(None)

import PIL as pil
from PIL import Image, ImageEnhance, ImageOps

from skimage.transform import warp
from skimage.registration import optical_flow_tvl1
from skimage.measure import regionprops, label
from skimage.feature import match_template
# import cv2

from scipy.ndimage import gaussian_filter, median_filter
from scipy.ndimage.morphology import binary_dilation, binary_erosion, generate_binary_structure
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import re

from Std_Tools import extendable_file as ex
from Std_Tools import read_image
from Std_Tools.conversion.dcm_nii import dcm2niix_by_files
from Std_Tools.data_mining.dcm_cardio import read_byte_array

def __split_str_by_capitals__(input_str):
    # re.findall('[A-Za-z]+[a-z]*', 'AC_CT_Head_Neck')
    # re.findall('[A-Z]+[a-z]*', 'AC_CT_HeadNeck')
    return re.findall('[A-Z]+[a-z]*',input_str)

def __get_crosshair__(size = 69,value = 255):
    container = np.zeros((size,size))
    half_size = math.ceil(size/2.0)
    container[half_size,:] = value
    container[:,half_size] = value
    return container

def examine_dcm_dir(dcm_dir):
    if not os.path.isdir(dcm_dir):
        raise IOError("dcm dir not exists")

    files = [os.path.join(dcm_dir,f) for f in os.listdir(dcm_dir)]

    df = pd.DataFrame()
    for f_i in range(len(files)):
        print("{0}/{1}".format(f_i+1,len(files)))
        f = files[f_i]
        try:
            D = dicom.read_file(f)
            dcm_dict = {}
            dcm_dict["SeriesDescription"] = D.SeriesDescription

            dcm_dict["path"] = f

            slice_loc = D.get([0x0020,0x1041])
            if not isinstance(slice_loc, NoneType):
                dcm_dict["SliceLocation"] = slice_loc.value
            else:
                dcm_dict["SliceLocation"] = None

            image_comments = D.get([0x0020,0x4000])
            if not isinstance(image_comments, NoneType):
                dcm_dict["ImageComments"] = image_comments.value
            else:
                dcm_dict["ImageComments"] = None


            dcm_dict["SeriesNumber"] = D.SeriesNumber
            dcm_dict["Modality"] = D.Modality

            df = df.append(dcm_dict, ignore_index = True)

        except Exception as e:
            print(str(e))

    df = df.sort_values(by=["SeriesNumber","SliceLocation"])

    return df

def separate_base_and_overlay(full_image):
    """
    returns the image layer - colored pixels replaced with neighbouring voxel's mean value - and the overlay mask
    :return:
    """

    full_image = Image.fromarray(full_image,"RGB")
    full_image = ImageOps.invert(full_image)
    # full_image.show()

    full_image = np.array(full_image)

    R,G,B = full_image[:,:,0],full_image[:,:,1],full_image[:,:,2]

    base_mask = np.logical_and(np.logical_and(R == G, G == B), B == R)
    overlay_mask = np.logical_not(base_mask).astype(int)

    base = np.copy(R)
    smoothed_base = median_filter(base,5)

    base_data =(((base * base_mask.astype(int)) + (smoothed_base*overlay_mask)))
    base_data_mask = base_data != 0
    filtered_base_mask = binary_dilation(binary_erosion(base_data_mask,iterations=5),iterations=0,mask=base_data_mask)
    base_data = base_data*filtered_base_mask

    # I = Image.fromarray(base_data.astype(np.uint8), "L")
    # I.show()
    # J = Image.fromarray(overlay_mask.astype(np.uint8)*255, "L")
    # J.show()

    return base_data, overlay_mask


def get_marker(overlay_image_data,point_dilation_count = 10):
    ch_size = 69
    ch_half_size =  math.ceil(ch_size/2.0)
    crosshair = __get_crosshair__(size=ch_size)

    res = match_template(overlay_image_data,crosshair)
    ij = np.unravel_index(np.argmax(res), res.shape)
    # x, y = ij[::-1]

    center_container = np.zeros_like(overlay_image_data)
    center_container[ij[0]+ch_half_size,ij[1]+ch_half_size] = 1
    center_container = binary_dilation(center_container, structure=generate_binary_structure(2,2), iterations=point_dilation_count)*255

    # I = Image.fromarray(np.stack([overlay_image_data*255, center_container , np.zeros_like(overlay_image_data)],axis=2).astype(np.uint8),"RGB")
    # I.show()

    return center_container

def get_marker_center(transformed_marker_array):
    try:
        marker_mask = np.array(transformed_marker_array)>0
        marker_props = regionprops(label(marker_mask))
        marker_props = sorted(marker_props, key= lambda X:X.bbox_area,reverse=True)[0]
        return np.array(marker_props.centroid)
    except Exception as e:
        print("transformed marker not found")
        return np.array([0,0])

def register_images(fix_img,moving_img,moving_marker):
    # return moving_img,moving_marker

    # --- Compute the optical flow
    v, u = optical_flow_tvl1(fix_img, moving_img, tightness = 0.05)

    # --- Use the estimated optical flow for registration
    nr, nc = fix_img.shape

    row_coords, col_coords = np.meshgrid(np.arange(nr), np.arange(nc),
                                         indexing='ij')

    moving_image_warp = warp(moving_img, np.array([row_coords + v, col_coords + u]),
                       mode='nearest')

    moving_marker_warp = warp(moving_marker, np.array([row_coords + v, col_coords + u]))

    return moving_image_warp, moving_marker_warp



def get_slice_matching_df(dicom_lookup_df, ref_data, overlay_data, thr = 5, global_scaler = False, base_dir = None):
    ref_image = Image.fromarray(ref_data.astype(np.uint8), "L")
    # I_ref.show()
    #bounding_box

    _bb = regionprops(label(np.array(ref_image)>thr))
    _bb = sorted(_bb, key=lambda X: X.bbox_area, reverse = True)
    _box = _bb[0].bbox
    _bbox = (_box[1],_box[0],_box[3],_box[2])
    # ref_image.show()
    ref_image = ref_image.crop(_bbox) #base image
    # ref_image.show()

    refm_data = get_marker(overlay_data)
    refm_image = Image.fromarray(refm_data.astype(np.uint8),"L")
    refm_image = refm_image.crop(_bbox) #marker image
    # refm_image.show()

    scale_factor = 2

    result_df = pd.DataFrame()
    dcm_files = list(dicom_lookup_df.path)
    out_nii_path = os.path.join(base_dir, "nii", "target_img.nii.gz")
    dcm2niix_by_files(dcm_files=dcm_files, out_nii=out_nii_path)
    _row = dicom_lookup_df.reset_index(drop=True).iloc[0]

    if ex(out_nii_path).exists():
        I = read_image(out_nii_path, reorient=True)

        if global_scaler:
            scaler = MinMaxScaler()
            scaler.fit(I.data.flatten()[:, np.newaxis])

        for slice_index in range(I.shape[2]):
            row = copy.copy(_row)
            slice = I.data[:, :, slice_index]
            slice = np.rot90(slice)
            img_shape = (I.shape[0], I.shape[1])

            if not global_scaler:
                scaler = MinMaxScaler()
                scaler.fit(slice.flatten()[:, np.newaxis])

            scaled = scaler.transform(slice.flatten()[:, np.newaxis])
            rescaled_slice = scaled.reshape(slice.shape) * np.array(ref_data).max()

            slice_image = Image.fromarray(rescaled_slice.astype(np.uint8), "L")

            __bb = regionprops(label(np.array(slice_image) > thr))
            __bb = sorted(__bb, key=lambda X: X.bbox_area, reverse=True)
            if len(__bb) == 0:
                continue

            __box = __bb[0].bbox
            __bbox = (__box[1], __box[0], __box[3], __box[2])
            slice_image = slice_image.crop(__bbox)
            slice_image = slice_image.resize((slice_image.size[0] * scale_factor, slice_image.size[1] * scale_factor))
            slice_image.transpose(Image.FLIP_LEFT_RIGHT)
            # slice_image.show()

            # match ref image to dicom
            _ref_image = ref_image.resize(slice_image.size)
            _refm_image = refm_image.resize(slice_image.size)

            _ref_data, _refm_data = register_images(fix_img=np.array(slice_image), moving_img=np.array(_ref_image),
                                                    moving_marker=np.array(_refm_image))
            _ref_data = _ref_data * np.array(slice_image).max()
            _refm_data = _refm_data * np.array(slice_image).max()

            # calculate similarity
            corr_mat = np.corrcoef(np.array(slice_image).flatten(), _ref_data.flatten())
            corr_val = corr_mat[0, 1]
            # print(corr_val)
            row["corr_val"] = corr_val

            # calculate world coordinate for maker
            # inter slice pixel location - swap dims with indexing
            marker_center = get_marker_center(_refm_data)
            bbox_translation = [__bbox[0], __bbox[1]]
            transformed_center = np.array(img_shape) - (
                        (marker_center / float(scale_factor)) + np.array(bbox_translation)) - 1
            transformed_center = transformed_center[::-1]
            marker_vox_coord = np.array(list(transformed_center) + [slice_index])
            row["marker_vox_loc"] = marker_vox_coord
            v = np.round(marker_vox_coord)
            row["marker_val"] = I.data[int(v[0]),int(v[1]),int(v[2])]
            row["marker_world_loc"] = np.array(I.voxel_2_world(marker_vox_coord))

            result_df = result_df.append(row, ignore_index=True)

        I.save(I.img_path)

    return result_df


def locate_markers(dicom_lookup_df, marker_image_sd, base_dir = None, global_scaler = False, thr = 5 ):
    if not isinstance(dicom_lookup_df,pd.DataFrame):
        raise TypeError

    marker_images = dicom_lookup_df[dicom_lookup_df["SeriesDescription"] == marker_image_sd]
    PET_images = dicom_lookup_df[dicom_lookup_df["Modality"] == "PT"]

    result_df = pd.DataFrame()

    # for index, row in marker_images.tail(1).iterrows():
    for index, row in marker_images.iterrows():
        print("Processing marker file {0}".format(row["path"]))

        _mask = __split_str_by_capitals__(row["ImageComments"])

        _PET_images = PET_images.copy()
        _PET_images["HIT"] = _PET_images["SeriesDescription"].apply(lambda X: len(list(set(__split_str_by_capitals__(X)).intersection(set(_mask)))))

        max_hit = np.max(_PET_images["HIT"])

        _target_images = _PET_images[_PET_images["HIT"]==max_hit]

        annot_dcm = dicom.read_file(row["path"])
        full_image = annot_dcm.pixel_array

        # I = Image.fromarray(full_image,"RGB")
        # I.show()

        base_layer, overlay = separate_base_and_overlay(full_image)

        matching_df = get_slice_matching_df(_target_images, ref_data = base_layer, overlay_data = overlay, base_dir=base_dir, global_scaler = global_scaler, thr = thr)
        best_slice = matching_df.sort_values(by="corr_val",ascending=False).reset_index(drop=True).iloc[0]

        print(best_slice)

        _res = {"MarkerSD":row["SeriesDescription"],"MarkerSN":int(row["SeriesNumber"]),"MarkerMod":row["Modality"],
                "MarkerImageComments":row["ImageComments"], "MarkerPath": row["path"],
                "PetSD":best_slice["SeriesDescription"],"PetSN":int(best_slice["SeriesNumber"]),
                "WorldLoc":best_slice["marker_world_loc"],"VoxLoc":best_slice["marker_vox_loc"],
                "PetVal":best_slice["marker_val"],"RegCorr":best_slice["corr_val"],
                "PetPath":best_slice["path"]}

        result_df = result_df.append(_res,ignore_index=True)

    return result_df

def extract_marker_info(base_dir, global_scaler = False, thr = 5 ):
    dcm_dir = os.path.join(base_dir,"dcm")
    dicom_lookup_csv = os.path.join(base_dir,"dcm_lookup.csv")

    # dicom_df = examine_dcm_dir(dcm_dir)
    # dicom_df.to_csv(dicom_lookup_csv,index=False)
    dicom_df = pd.read_csv(dicom_lookup_csv)

    marker_image_sd = "Results MM Oncology Reading"
    marker_result_df = locate_markers(dicom_df,marker_image_sd, base_dir= base_dir, global_scaler = global_scaler, thr = thr)

    marker_csv = os.path.join(base_dir, "markers.csv")
    marker_result_df.to_csv(marker_csv, index=False)

def main():
    # base_dir = "/nas/medicopus_share/Projects/SygoMarker/PTCT016639/"
    base_dir = "/nas/medicopus_share/Projects/SygoMarker/phantomTest1"
    extract_marker_info(base_dir, global_scaler= False, thr= 10)



if __name__ == '__main__':
    main()