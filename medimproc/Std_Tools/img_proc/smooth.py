#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import math
import nibabel.processing as nproc
from scipy import ndimage as ndi
sys.path.insert(0,'/home/fajtai/py/')

from Std_Tools.img_proc.IO.img_reader import read_image
from Std_Tools.common.command_runner.command_runner import CommandRunner

def fwhm_2_sigma(fwhm):
    sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
    return sigma

def img_smooth(img,fwhm):
    if not(hasattr(img,"dataobj") and hasattr(img,"affine") and hasattr(img,"header") and hasattr(img,"shape")):
        raise TypeError("not valid nibabel image")
    out_img = nproc.smooth_image(img,fwhm,mode='nearest')
    return out_img

def get_smoothed_nii(nii_file,fwhm,):
    if not os.path.exists(nii_file):
        raise IOError("Error! File {0} not exists!".format(str(nii_file)))

    I = read_image(nii_file)
    smoothed_img = img_smooth(I.img,fwhm)
    I.img = smoothed_img
    I._data = I.get_data()
    return I


def gaussian_smoothing(niiData,fwhm):
    '''
    In program smoothing
    :param niiData: data from a nii file
    :param fwhm: FWHM in mm
    :return: smoothed data
    '''
    #todo voxel méretek figyelembe vétele!
    sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
    outData = ndi.gaussian_filter(niiData, sigma)

    return outData

def fslGaussianSmooth(niiFile, fwhm, outNii, autoRun=True, verbose = True):
    '''
    Command line smoothing with fslmaths\n
    :param niiFile: nifti image
    :param fwhm: FWHM in mm
    :param autoRun: Run the generated command
    :return: smoothed nii image
    '''
    if fwhm ==0:
        return dict([("outNii",niiFile)])
    sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
    command = "fslmaths " + niiFile + " -s " + str(sigma) + " " + outNii
    C = CommandRunner()
    C.Commands.append([command, outNii])
    if autoRun:
        C.run()
    return C
