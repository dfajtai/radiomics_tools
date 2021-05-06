#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from NiiTools import NiiBasics as nb
from ImgProc import *
import numpy as np
from scipy import ndimage

import matplotlib
import matplotlib.pyplot as plt


import SimpleITK as sitk
from ImgProc.itk_show_img import *



def get_indices_from_labeling(data,index):
    """
    :param data: binary matrix
    :param index: returned labels value
    :return:
    """
    ldata,max_index = labelData(data)
    mask_indices = ldata==index
    return mask_indices


def get_inner_max_pos(seed,data_mtx):
    """
    :param seed: true false matrix
    :type seed: np.ndarray
    :param data_mtx: data matrix
    :type data_mtx: np.ndarray
    :return:
    """
    seed= seed.astype("int")
    masked_data = data_mtx*seed

    max_pos = np.unravel_index(np.nanargmax(masked_data),masked_data.shape)

    return max_pos


def show_pic_with_label(img,label_img,coord_list,title=""):
    img_255 = sitk.Cast(sitk.RescaleIntensity(img), sitk.sitkUInt8)
    myshow3d(sitk.LabelOverlay(img_255, label_img), xslices = [coord_list[0]], yslices = [coord_list[1]], zslices = [coord_list[2]], title=title)


def connected_threshold(img_path,coord_list,lower=0,upper = 1000):
    if not os.path.exists(img_path):
        return

    img = sitk.ReadImage(img_path)

    seg = sitk.Image(img.GetSize(), sitk.sitkUInt8)
    seg.CopyInformation(img)
    seg[coord_list]=1
    seg = sitk.BinaryDilate(seg,1)
    seg_con = sitk.ConnectedThreshold(img, seedList=[coord_list],  lower=lower, upper=upper)

    return img,seg_con


def confidence_connected_reg_growth(img_path,coord_list,numberOfIterations=1, multiplier=2.5,
                                        initialNeighborhoodRadius=1,replaceValue=1):
    if not os.path.exists(img_path):
        return

    img = sitk.ReadImage(img_path)

    seg_conf = sitk.ConfidenceConnected(img, seedList=[coord_list], numberOfIterations=numberOfIterations, multiplier=multiplier,
                                        initialNeighborhoodRadius=initialNeighborhoodRadius, replaceValue=replaceValue)
    return img,seg_conf

def vector_conf_connected(img_path,img_path_2,coord_list,numberOfIterations=1, multiplier=4,
                                        initialNeighborhoodRadius=1):
    if not os.path.exists(img_path):
        return

    img = sitk.ReadImage(img_path)

    img2 = sitk.ReadImage(img_path_2)

    img_multi= sitk.Compose(img,img2)
    seg_vec = sitk.VectorConfidenceConnected(img_multi,seedList=[coord_list],numberOfIterations=numberOfIterations, multiplier=multiplier,
                                        initialNeighborhoodRadius=initialNeighborhoodRadius)

    return img,seg_vec

def fill_holes(seg):
    vectorRadius = (1, 1, 1)
    kernel = sitk.sitkBall
    seg_clean = sitk.BinaryMorphologicalClosing(seg,vectorRadius,
                                            kernel)
    return seg_clean


def remove_small_elements(seg):
    vectorRadius = (1, 1, 1)
    kernel = sitk.sitkBall
    seg_clean = sitk.BinaryMorphologicalOpening(seg, vectorRadius,
                                                kernel)
    return seg_clean

def main():
    img1_path = "/data/clinics/p001/rfmri/clean-am-p001-rfmri-1.nii"

    coord = [58,32,28]
    # img, reg = confidence_connected_reg_growth(img1_path,coord,1,3.6)
    img, reg = connected_threshold(img1_path, coord, lower=900, upper= 20000)
    show_pic_with_label(img,remove_small_elements(reg),coord)

if __name__ == '__main__':
    main()