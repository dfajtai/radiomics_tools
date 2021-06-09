#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os,sys

NoneType = type(None)

import glob
import numpy as np

from Std_Tools.common.py_io import py_copy, py_remove, py_mkdirs, py_link

from Std_Tools.img_proc.bounding_box import bbox_3d_with_iso_border, box_crop_fix

from Std_Tools import extendable_file as ex
from Std_Tools import NibImg, read_image

from Std_Tools.registration.fsl_affine import flirt_register, flirt_apply_xfm
from Std_Tools.img_proc.resampling import nibabel_resampling_like, flirt_resample, mri_convert_resample


def stack_images(images, out_dir, axis = 0, height = 145, displacement_matrix_val = -1024.0, mask_thr = 0):

    images = sorted(images)

    preprocessed_paths = []

    if not os.path.isdir(out_dir):
        py_mkdirs(out_dir)

    main_img_path = images[0]
    main_img_ext_path = os.path.join(out_dir, "ext-{0}.gz".format(os.path.basename(main_img_path)))
    main_img_ext_mask_path = os.path.join(out_dir, "ext_mask-{0}.gz".format(os.path.basename(main_img_path)))

    main_img = read_image(main_img_path)

    #remove table
    main_img.data[:, :height, :] = displacement_matrix_val

    #create mask
    mask = main_img.data>mask_thr

    #extend img
    displacement_matrix = np.ones_like(main_img.data) * displacement_matrix_val

    origin_displacement = np.array([0] * 3)
    origin_displacement[axis] = displacement_matrix.shape[axis] * main_img.step_sizes[axis]
    main_img.affine_origin = main_img.affine_origin - origin_displacement

    main_img.data = np.concatenate((displacement_matrix, main_img.data, displacement_matrix), axis=axis).astype(np.int16)

    main_img.save(main_img_ext_path,dtype="int16")

    #extend mask
    main_img.data = np.concatenate((np.zeros_like(mask), mask.astype(np.int), np.zeros_like(mask)), axis=axis).astype(np.uint8)
    main_img.save(main_img_ext_mask_path,dtype="uint8")

    for i in images[1:]:
        mask_path =os.path.join(out_dir, "mask-{0}.gz".format(os.path.basename(i)))

        I = read_image(i)

        #remove table
        I.data[:,:height,:] = displacement_matrix_val
        #create mask
        I.to_bin(low=mask_thr)
        I.data = I.data.astype(np.uint8)
        I.save(mask_path,dtype="uint8")
        preprocessed_paths.append({"img":i,"mask":mask_path})


    ref = main_img_ext_path
    ref_mask = main_img_ext_mask_path

    concatenated_image = read_image(ref)
    concatenated_data = concatenated_image.data

    for preproc_path in preprocessed_paths:
        moving_img = preproc_path["img"]
        moving_mask = preproc_path["mask"]

        #registration
        mat_path = os.path.join(out_dir, "trf-{0}.mat".format(os.path.basename(moving_img)))
        reg_path = os.path.join(out_dir, "reg-{0}".format(os.path.basename(moving_img)))
        reg_mask_path = os.path.join(out_dir, "reg-{0}".format(os.path.basename(moving_mask)))

        #straightforward registion
        # flirt_register(input=moving_img,ref = ref,out_mat=mat_path,out_nii=reg_path,dof = 6,search=[-5,5], refweref_maskight = ref_mask,inweight = moving_mask)

        #registration via mask matching
        flirt_register(input=moving_mask,ref = ref_mask,out_mat=mat_path,out_nii=reg_mask_path,dof = 6,search=[-5,5], interp="nearestneighbour")
        flirt_apply_xfm(input=moving_img,ref= moving_mask,mat_file = mat_path,out_nii=reg_path)

        #concatenate_images
        I = read_image(reg_path)
        _C = I.data[np.newaxis,...]
        C = np.concatenate((concatenated_data[np.newaxis,...],_C),axis=0)
        concatenated_data = np.max(C,axis=3)

    #box crop final image
    final_img_path = os.path.join(out_dir,"final_img.nii.gz")

    concatenated_image.data = concatenated_data
    concatenated_mask = concatenated_image.data>mask_thr

    p1, p2 = bbox_3d_with_iso_border(concatenated_mask, 20)
    p1w = concatenated_image.voxel_2_world(p1)
    p2w = concatenated_image.voxel_2_world(p2)

    concatenated_image = box_crop_fix(concatenated_image, p1w, p2w)
    concatenated_image.save(final_img_path)


def main():
    imgs = glob.glob("/home/fajtai/test/multi_image/*.nii")
    stack_images(imgs, "/home/fajtai/test/multi_image/result/")
    pass

if __name__ == '__main__':
    main()