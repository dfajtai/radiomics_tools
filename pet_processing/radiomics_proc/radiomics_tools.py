#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import math
import pandas as pd
import copy
import re
import numpy as np
import pydicom as dicom
from datetime import datetime

import skimage as sk
import SimpleITK as sitk

import radiomics
from radiomics import featureextractor, glrlm, glcm, shape
from radiomics import base

from Std_Tools.common.py_io import *
from Std_Tools.common.colorPrint import *
from .radiomics_normalize import normalize_AR, normalize_LAR


def sitk_to_np(in_img):
    # type: (sitk.Image) -> tuple[np.ndarray, tuple[float, float, float]]
    return sitk.GetArrayFromImage(in_img), in_img.GetSpacing()


def extract_radiomics_features(image_path, mask_path, mask_name="radiomics"):
    image_path = str(image_path)
    mask_path = str(mask_path)

    printCaption("Radiomics over image {0}, mask {1}".format(image_path,mask_path))

    if not os.path.isfile(image_path):
        return False
    if not os.path.isfile(mask_path):
        return False

    img = sitk.ReadImage(image_path)
    mask = sitk.ReadImage(mask_path)

    stat_filter = sitk.StatisticsImageFilter()
    stat_filter.Execute(mask)
    max_value = stat_filter.GetMaximum()
    if max_value==0:
        printWarning("Mask '{0}' is empty".format(mask_path))
        return {}

    printCommand("Radiomics feature extraction started...")
    radiomics.setVerbosity(20)
    f_e = featureextractor.RadiomicsFeatureExtractor()

    f_e.enableAllFeatures()
    computed_features = f_e.computeFeatures(img,mask,mask_name)
    printCommand("Radiomics feature extraction done...")

    return dict(computed_features)



if __name__ == '__main__':
    # img = "/data/dopa-onco/radiomics_test/petct-rad/petct/ctacPET.nii"
    # mask = "/data/dopa-onco/radiomics_test/petct-rad/petct/mask.nii"

    mask = "/data/dopa-onco/p001/pet/CL01S-p001_01-pet-vibe.nii"
    img = "/data/dopa-onco/p001/pet/S-p001_01-pet-vibe.nii"

    print(extract_radiomics_features(img,mask))
    pass
