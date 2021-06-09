#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np

import scipy.ndimage as ndimage

sys.path.insert(0, '/home/fajtai/py/')

from NiiTools import NiiBasics as nb

import SimpleITK as sitk
from ImgProc.itk_show_img import *


def find_3d_minmax_pos_val(data,start,arg_function=np.argmax,border=2):
    if not isinstance(data,np.ndarray):
        return start

    x_min = max(start[0]-border,0)
    x_max = min(start[0]+border+1,data.shape[0]-1)
    y_min = max(start[1]-border,0)
    y_max = min(start[1]+border+1,data.shape[1]-1)
    z_min = max(start[2]-border,0)
    z_max = min(start[2]+border+1,data.shape[2]-1)

    _reg = data[x_min:x_max,y_min:y_max,z_min:z_max]

    pos = np.unravel_index(arg_function(_reg),_reg.shape)
    pos = tuple(pos+ np.array(start)-border)

    val = data[pos]

    return pos, val

def dilate_growth(low_data,high_data,start,A=1.5,B=0.6,V=0.95):
    if not isinstance(low_data,np.ndarray):
        return
    if not isinstance(high_data,np.ndarray):
        return

    high_image = sitk.GetImageFromArray(np.swapaxes(high_data,0,2))
    high_image_2_show = sitk.Cast(sitk.RescaleIntensity(high_image),sitk.sitkUInt8)
    kernel = ndimage.generate_binary_structure(3,1).astype(int)

    initial_mask = np.zeros(low_data.shape).astype("uint8")

    diff_max_pos, diff_max = find_3d_minmax_pos_val(high_data-low_data,start,np.argmax,2)

    # low_min_pos, low_min = find_3d_minmax_pos_val(low_data,start,np.argmin,2)
    # high_max_pos, high_max = find_3d_minmax_pos_val(high_data,start,np.argmax,2)

    low_min = low_data[diff_max_pos]
    high_max = high_data[diff_max_pos]

    initial_mask[diff_max_pos] = 1
    run = True
    nprev =0
    i = 0

    while run == True:
        print("iteration {0}".format(str(i + 1)))
        dilated = ndimage.binary_dilation(initial_mask, structure=kernel, iterations=1).astype("uint8") - initial_mask

        high_dilated = high_data * (dilated == 1).astype("uint8")
        high_filtered = (high_dilated > high_max * B)

        low_dilated = low_data * (dilated == 1).astype("uint8")
        low_filtered = (low_dilated < low_min * A)

        new_growth = np.logical_and(high_filtered, low_filtered)
        n = np.sum(new_growth)

        if n <= nprev * V:
            run = False
        else:
            nprev = n
            initial_mask[new_growth] = 1
            i += 1

            # show image
            # label_image = sitk.GetImageFromArray(np.swapaxes(initial_mask, 0, 2))
            # myshow3d(sitk.LabelOverlay(high_image_2_show, label_image), xslices=[start[0]], yslices=[start[1]],
            #          zslices=[start[2]], title="iteration {0}".format(str(i)))
            print(n)

    label_image = sitk.GetImageFromArray(np.swapaxes(initial_mask, 0, 2))
    myshow3d(sitk.LabelOverlay(high_image_2_show, label_image), xslices=[start[0]], yslices=[start[1]],
             zslices=[start[2]], title="Region after the {0}th iteration".format(str(i)))
    print("Done")


def limited_dilate_growth(growth_limiter,low_data,high_data,start,A,B,show_final= True):
    if not isinstance(low_data,np.ndarray):
        return
    if not isinstance(high_data,np.ndarray):
        return

    kernel = ndimage.generate_binary_structure(3,1).astype(int)
    high_image = sitk.GetImageFromArray(np.swapaxes(high_data,0,2))
    high_image_2_show = sitk.Cast(sitk.RescaleIntensity(high_image),sitk.sitkUInt8)

    initial_mask = np.zeros(low_data.shape).astype("uint8")

    diff_max_pos, diff_max = find_3d_minmax_pos_val(high_data-low_data,start,np.argmax,2)

    low_min = low_data[diff_max_pos]
    high_max = high_data[diff_max_pos]

    initial_mask[diff_max_pos] = 1
    run = True

    i = 0

    n_match = 1
    n_miss = 0

    while run == True:
        print("iteration {0}".format(str(i + 1)))
        dilated = ndimage.binary_dilation(initial_mask, structure=kernel, iterations=1).astype("uint8") - initial_mask

        high_dilated = high_data * (dilated == 1).astype("uint8")
        high_filtered = (high_dilated > high_max * B)

        low_dilated = low_data * (dilated == 1).astype("uint8")
        low_filtered = (low_dilated < low_min * A)

        new_growth = np.logical_and(high_filtered, low_filtered)

        # new_growth = dilated.astype("bool")

        n = np.sum(new_growth)

        new_match = np.sum(np.logical_and(new_growth,growth_limiter))
        new_miss = n-n_match

        if n_miss+new_miss>n_match+new_match:
            run = False
        else:
            n_miss += new_miss
            n_match += new_match

            initial_mask[new_growth] = 1
            i += 1

            # show image
            # label_image = sitk.GetImageFromArray(np.swapaxes(initial_mask, 0, 2))
            # myshow3d(sitk.LabelOverlay(high_image_2_show, label_image), xslices=[start[0]], yslices=[start[1]], zslices=[start[2]], title="iteration {0}".format(str(i)))
            print(n)

    if show_final:
        label_image = sitk.GetImageFromArray(np.swapaxes(initial_mask, 0, 2))
        img = sitk.LabelOverlay(high_image_2_show, label_image)
        myshow3d(img, xslices=[start[0]], yslices=[start[1]], zslices=[start[2]], title="Region after the {0}th iteration".format(str(i)))
        # myshow3d(img, xslices=[46], yslices=[84], zslices=[153], title="Region after the {0}th iteration".format(str(i)))
    print("Done")

    return initial_mask


def main():
    t1_path = "/home/fajtai/py/SmStudy/Lesion_Growth/test/p005-t1-1.nii"
    flair_path = "/home/fajtai/py/SmStudy/Lesion_Growth/test/rmp005-flair-1.nii"

    t1_data=nb.readNii(t1_path)["data"]
    flair_data = nb.readNii(flair_path)["data"]

    dilate_growth(t1_data,flair_data,(43,84,152),A=1.5,B=0.6,V=0.95)
    # dilate_growth(t1_data,flair_data,(72,79,181),A=1.5,B=0.6,V=0.95)

if __name__ == '__main__':
    main()