# -*- coding: utf-8 -*-

import numpy as np
import os, sys
import SimpleITK as sitk
import radiomics

from radiomics import featureextractor, firstorder, glcm, gldm, glrlm, glszm, ngtdm, shape

import six

import logging
# from contextlib import suppress

from Std_Tools.common.colorPrint import *


def getAllTextureDescriptors(image, mask, bin_width):
    """
    `image` and `mask` must be ITK images
    """

    if not isinstance(image,sitk.Image):
        raise TypeError

    if not isinstance(mask,sitk.Image):
        raise TypeError

    allFeatures = {}

    firstOFeatures = radiomics.firstorder.RadiomicsFirstOrder(image, mask)
    firstOFeatures.enableAllFeatures()
    firstOFeatures.execute()
    for (key,val) in six.iteritems(firstOFeatures.featureValues):
        allFeatures['firstorder_' + key] = val

    glrmFeatures = radiomics.glrlm.RadiomicsGLRLM(image, mask, binWidth = bin_width)
    glrmFeatures.enableAllFeatures()
    glrmFeatures.execute()
    for (key,val) in six.iteritems(glrmFeatures.featureValues):
        allFeatures['glrm_' + key] = val

    glszmFeatures = radiomics.glszm.RadiomicsGLSZM(image, mask, binWidth = bin_width)
    glszmFeatures.enableAllFeatures()
    glszmFeatures.execute()
    for (key,val) in six.iteritems(glszmFeatures.featureValues):
        allFeatures['glszm_' + key] = val

    glcmFeatures = radiomics.glcm.RadiomicsGLCM(image, mask, binWidth = bin_width)
    glcmFeatures.enableAllFeatures()
    glcmFeatures.execute()
    for (key,val) in six.iteritems(glcmFeatures.featureValues):
        allFeatures['glcm_' + key] = val

    gldmFeatures = radiomics.gldm.RadiomicsGLDM(image, mask, binWidth = bin_width)
    gldmFeatures.enableAllFeatures()
    gldmFeatures.execute()
    for (key,val) in six.iteritems(gldmFeatures.featureValues):
        allFeatures['gldm_' + key] = val

    ngtdmFeatures = radiomics.ngtdm.RadiomicsNGTDM(image, mask, binWidth = bin_width)
    ngtdmFeatures.enableAllFeatures()
    ngtdmFeatures.execute()
    for (key,val) in six.iteritems(ngtdmFeatures.featureValues):
        allFeatures['ngtdm_' + key] = val

    return allFeatures

def __get_features__(image,mask,bin_width, label_val = 1):
    if not isinstance(image,sitk.Image):
        raise TypeError

    if not isinstance(mask,sitk.Image):
        raise TypeError


    # printCommand("Radiomics feature extraction started...")
    logging.raiseExceptions = False

    extractor = featureextractor.RadiomicsFeatureExtractor(binWidth = bin_width, label = label_val)
    extractor.enableAllFeatures()

    radiomics.setVerbosity(60)

    result = None
    result_dict = {}

    # with suppress(Exception):
    result = extractor.execute(image, mask)
        # pass

    logging.raiseExceptions = True
    # printCommand("Radiomics feature extraction done...")

    if isinstance(result,type(None)):
        return result_dict

    for key,value in six.iteritems(result):
        if not str(key).startswith("diagnostics"):
            result_dict[str(key).replace("original_","")] = value

    return result_dict


def extract_radiomics_features(image_path, mask_path, bin_width=0.1, label_val = None):
    if isinstance(image_path,sitk.Image):
        img = image_path
    else:
        image_path = str(image_path)
        if not os.path.isfile(image_path):
            return False
        img = sitk.ReadImage(image_path)

    if isinstance(mask_path,sitk.Image):
        mask = mask_path
    else:
        mask_path = str(mask_path)
        if not os.path.isfile(mask_path):
            return False

        mask = sitk.ReadImage(mask_path)

    if isinstance(label_val,type(None)):
        label_val = 1

    if all([isinstance(p, str) for p in [image_path,mask_path]]):
        printCaption("Radiomics over image {0}, mask {1}".format(image_path,mask_path))

    stat_filter = sitk.StatisticsImageFilter()
    stat_filter.Execute(mask)
    max_value = stat_filter.GetMaximum()
    if max_value==0:
        if isinstance(mask_path,str):
            printWarning("Mask '{0}' is empty".format(mask_path))
        else:
            printWarning("Mask is empty")
        return {}

    printCommand("Radiomics feature extraction started on label {0}...".format(label_val))

    _result = __get_features__(img,mask,bin_width = bin_width, label_val = label_val)

    result={}

    for key,value in six.iteritems(_result):
        if not str(key).startswith("diagnostics"):
            result["{0}_{1}".format("radiomics",key)] = value
    return result


if __name__ == '__main__':
    # img = "/data/dopa-onco/radiomics_test/petct-rad/petct/ctacPET.nii"
    # mask = "/data/dopa-onco/radiomics_test/petct-rad/petct/mask.nii"

    img = "/data/dopa-onco/p001/pet/CL01S-p001_01-pet-vibe.nii"
    mask = "/data/dopa-onco/p001/pet/S-p001_01-pet-vibe.nii"

    print(extract_radiomics_features(img,mask))
    pass
