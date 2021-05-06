#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from nibabel.processing import resample_from_to

import numpy as np
import SimpleITK as sitk

NoneType = type(None)

sys.path.insert(0,'/home/fajtai/py/')
from Common.CommandRunner import CommandRunner
from Common.colorPrint import *

from Std_Tools._package_opts_ import *
from Std_Tools.img_proc.IO.img_reader import read_image, NibImg


def mri_convert_resample(inFile ="", refFile ="", outFile ="", overwrite = None, **kwargs):
    """
    Run mri-convert --like
    :param input: input file
    :param reference: size reference image
    :param output: output file
    :return: command
    """
    inFile = str(inFile)

    if isinstance(overwrite,NoneType):
        overwrite = CommandRunner.overwrite

    if os.path.exists(inFile):
        if refFile != "":
            command = "mri_convert --like {0} {1} {2}".format(str(refFile),str(inFile),str(outFile))
        else:
            command = "mri_convert {0} {1}".format(str(inFile), str(outFile))

        for k in kwargs.keys():
            command += " --{0} {1}".format(str(k), str(kwargs[k]))

        C = CommandRunner()
        C.overwrite = overwrite
        C+=[command,outFile]
        C.run()
    else:
        printWarning("Warning! File '{0}' not exists!".format(str(inFile)))

def flirt_resample(input,out_nii,iso_size=1,interp="trilinear"):
    command = flirtPath +" -in {input} -ref {ref} -out {out}".format(input = str(input),ref = str(input), out = str(out_nii))

    command += " -applyisoxfm " + str(iso_size)

    if interp in flirt_interpTypes:
        command += " -interp " + interp

    C = CommandRunner()
    C += [command, [str(out_nii)]]
    C.run()


def nibabel_resampling_like(input,like,output=None, interp = 1):
    """
    :param input: input nib image or image path
    :param like: 'like' nib image or image path
    :param output: output path
    :param interp: 1 - trilinear, 3 - spline
    :return: resampled nib image
    """
    if isinstance(input,str):
        input = read_image(input)
    if not isinstance(input, NibImg):
        return

    if isinstance(like,str):
        like = read_image(like)
    if not isinstance(like, NibImg):
        return

    resampled = input.resample_like(img_like=like,interp=interp,inplace=False)

    if output and output!= "":
        resampled.save(output)
    return resampled


def nibabel_resampling_to_voxel_size(input,voxel_sizes,output="", interp = 1):
    """
    :param input: input nib image or image path
    :param voxel_sizes: voxel sizes in array, or scalar for isometric scale
    :param output: output path
    :param interp: 1 - trilinear, 3 - spline
    :return: resampled nib image
    """
    # http://nipy.org/nibabel/reference/nibabel.processing.html#nibabel.processing.resample_to_output

    raise NotImplementedError


def resample_img_sitk(itk_image, out_spacing=[2.0, 2.0, 2.0], is_label=False):
    # Resample images to 2mm spacing with SimpleITK
    original_spacing = itk_image.GetSpacing()
    original_size = itk_image.GetSize()

    out_size = [
        int(np.round(original_size[0] * (original_spacing[0] / out_spacing[0]))),
        int(np.round(original_size[1] * (original_spacing[1] / out_spacing[1]))),
        int(np.round(original_size[2] * (original_spacing[2] / out_spacing[2])))]

    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(out_spacing)
    resample.SetSize(out_size)
    resample.SetOutputDirection(itk_image.GetDirection())
    resample.SetOutputOrigin(itk_image.GetOrigin())
    resample.SetTransform(sitk.Transform())
    resample.SetDefaultPixelValue(itk_image.GetPixelIDValue())

    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)