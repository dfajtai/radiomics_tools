#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pet image cropping functions
"""

import sys

sys.path.insert(0, '/home/fajtai/py/')

from Std_Tools.img_proc.labeling import *
from Std_Tools.img_proc.bounding_box import *
from Std_Tools.common import CommandRunner
from Std_Tools.common.colorPrint import *
from Std_Tools.img_proc.IO.img_reader import read_image
from Std_Tools.StudyHelper.path_handler import extendable_file as ex

# from Std_Tools import extendable_file as ex



def fdg_brain_mask(pet_data,percentile = 95,size_filter = 1000, **kwargs):
    """
    Calculating brain mask from FGD image.
    :param pet_data: pet image data
    :param percentile: percentile for high pass filtering image data
    :param size_filter: minimal island size limit after threshold
    :param kwargs: ...
    :return: binary brain mask
    """
    #filtering with percentile
    p = np.percentile(pet_data[pet_data > 0], percentile)
    indices = pet_data > p

    mean = np.mean(pet_data[indices])
    sd = np.std(pet_data[indices])

    #filtering with mean, sd
    indices = pet_data > mean - sd

    m_pet = np.zeros_like(indices)
    m_pet[indices] = 1
    m_pet = m_pet * pet_data

    labeled_data, num_of_labels = labelData(m_pet)
    brain_mask = np.zeros_like(pet_data)
    max_label_size = 0

    for l in range(1, num_of_labels):
        label_size = np.sum(labeled_data == l)
        if label_size >= size_filter:
            if label_size >= max_label_size*0.25:
                brain_mask[labeled_data == l] = 1
            if label_size>max_label_size:
                max_label_size = label_size

    return brain_mask


def pet_box(pet_path, brain_mask_function, save_mask = False, **kwargs):
    """
    calculating bounding box for a given pet image based on a brain mask
    :param pet_path: pet image path
    :param brain_mask_function: brain mask function: F(pet_data,**kwargs)
    :param save_mask: option for saving brain mask used to estimate bounding box
    :param kwargs: extra parametres for brain_mask_function
    :return: bounding box parameters: [[p1w,p2w], new_size, [p1,p2]]
    """
    printInfo("Calculating pet bounding box for fdg-pet image")

    if not CommandRunner.runSwitch:
        return

    pet_nii = read_image(pet_path)
    if not pet_nii:
        return

    pet_mask = brain_mask_function(pet_nii.data,**kwargs)

    if save_mask:
        # raise NotImplementedError
        pet_mask_path = ex(pet_path)*"brain_mask-"
        pet_nii.data = pet_mask
        pet_nii.save(pet_mask_path)

    border = [30,30,25]
    p1,p2 = bbox_with_3_border(pet_mask,*border)

    new_size = tuple(np.array(p2)-np.array(p1))

    p1w, p2w = pet_nii.voxel_2_world(p1,ignore_negative_step=True), pet_nii.voxel_2_world(p2,ignore_negative_step=True)

    return [p1w, p2w], new_size, [p1, p2]

def pet_box_crop(pet_path,out_path,pet_box):
    """
    :param pet_path: pet input path
    :param out_path: cropped pet output path
    :param pet_box: bounding box parameters: [[p1w,p2w], new_size, [p1,p2]]
    :return:
    """
    printInfo("Cropping fdg based pet image '{0}' -> '{1}' ...".format(pet_path,out_path))

    if not CommandRunner.runSwitch:
        return

    pw, s, p = pet_box
    I = box_crop_relative(pet_path,pw[0],s,pw[0])
    I.save(out_path)


def img_box_crop(img_path,out_path,pet_box):
    """
    :param img_path: image input path
    :param out_path: image output path
    :param pet_box: bounding box parameters: [[p1w,p2w], new_size, [p1,p2]]
    :return:
    """
    pw, s, p = pet_box
    I = box_crop_fix(img_path, pw[0], pw[1], pw[0])
    I.save(out_path)
