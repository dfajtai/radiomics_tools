#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys

import numpy as np
import math

import scipy.ndimage as ndimage
import scipy.ndimage.measurements as meas
from scipy.ndimage.morphology import binary_closing, binary_propagation, binary_erosion

import pandas as pd

from ImgProc.dilate import dilate, erode
from ImgProc.labeling import labeling_data_with_counts
from Std_Tools.img_proc.custom_kernels import spherical_kernel
from Std_Tools.StudyHelper import extendable_file as ex
from Std_Tools.img_proc.IO.img_reader import read_image, NibImg
from Std_Tools.img_proc.labeling import labeling_data_with_counts
from Std_Tools.img_proc.bounding_box import bbox_3d_with_iso_border, box_crop_fix_voxel

mask_path = "/dani/ors/Segmentation-label.nii"

img_path = "/dani/ors/frontale.nii"

label_filled_bone = "/dani/ors/label_filled_bone.nii"
grad_bone = "/dani/ors/grad_bone.nii"

closed_bone = "/dani/ors/closed_bone.nii"
ero_prop_bone = "/dani/ors/EP_bone.nii"



def contour(img):
    d = img.data
    C = img.c()
    C.erode(N=3)
    C.data = d - C.data
    return C


def gradient(img, save_path=""):
    grad_img = img.c()
    grad = np.gradient(img.data)
    grad_mag = [np.linalg.norm(grad, axis=0)]
    grad_data = np.array(grad + grad_mag)

    print(grad_data.shape)

    if save_path != "":
        for i, c in zip(range(4), ["x", "y", "z", "m"]):
            grad_img.data = grad_data[i, :, :, :]
            grad_img.save(ex(save_path) * c)

    return grad_data


def label_fill_holes(img, save_path=""):
    if not isinstance(img, NibImg):
        return

    box = bbox_3d_with_iso_border(img.data, 3)
    box_crop_fix_voxel(img, p1=box[0], p2=box[1])

    labeled_background, counts = labeling_data_with_counts(img.data == 0)

    filled_bone = np.zeros_like(img.data)
    for v, c in counts[1:]:
        print((v, c))
        filled_bone[labeled_background == v] = 1

    labeled_filled_img = img.c()
    labeled_filled_img.data = filled_bone
    if save_path != "":
        labeled_filled_img.save(save_path, dtype="uint8")

    return labeled_filled_img


def hole_close(img, kernel=None, save_path=""):
    if kernel is None:
        img.data = binary_closing(img.data, iterations=5)
    else:
        img.data = binary_closing(img.data, iterations=1, structure=kernel)
    if save_path != "":
        img.save(save_path, dtype="uint8")
    return img


def ero_prop(img, save_path=""):
    D = np.logical_not(img.data)
    eroded = binary_erosion(D, iterations=10)
    D = binary_propagation(eroded, mask=D)
    img.data = np.logical_not(D)
    if save_path != "":
        img.save(save_path, dtype="uint8")


def main():
    N = 3
    kernel = spherical_kernel(N=9)
    I = read_image(mask_path)

    for i in range(N):
        I = label_fill_holes(I, ex(label_filled_bone) * "N{0}".format(str(i + 1)))
        I = hole_close(I, kernel=kernel, save_path=ex(closed_bone) * "N{0}".format(str(i + 1)))


if __name__ == '__main__':
    main()