#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import math
import os, sys
import pydicom as dicom
from pydicom.multival import MultiValue
from pydicom.valuerep import PersonName3
import re
import numpy as np


from Std_Tools import extendable_file as ex
from Std_Tools import read_image
from Std_Tools import NibImg
from Std_Tools.common.colorPrint import *




def decay_corr_signal_from_dyn_img(img, time_scale, decay_factor=None):
    """
    Based on: 'Decay Correction Methods in Dynamic PET Studies - Kewei 1995' - Conventional decay correction technique 1.

    :param img:
    :param time_scale:
    :return:
    """

    if not isinstance(img, NibImg):
        img = read_image(img)

    if not isinstance(img,NibImg):
        raise TypeError

    if len(img.shape)!=4:
        printWarning("Input image is not 4 dimensional")
        raise TypeError

    if isinstance(decay_factor,type(None)):
        decay_factor = get_decay_factor()

    if img.shape[3]+1 != np.shape(time_scale)[0]:
        printWarning("Mismatch between image (len. of 4th dim + 1 = {0} ) and time scale (len = {1})".format(img.shape[3]+1,np.shape(time_scale)[0]))

    out_time_scale = []

    corr_data = np.zeros_like(img.data)

    for frame_index in range(img.shape[3]):
        t_1 = time_scale[frame_index]
        t_2 = time_scale[frame_index+1]

        t_i = (t_1+t_2)/2.0

        # pre_corr = img.data[:,:,:,time_index] / (t_2-t_1) #estimate middle of the frame...

        #frame middle estimation
        #function value approximation at t_i from integral of f(t) between t_1 and t_2
        est_factor_1 = 1.0/(t_2-t_1)

        pre_corr = img.data[:,:,:,frame_index] * est_factor_1

        factor = math.exp(decay_factor*t_i)

        corr = pre_corr * factor

        out_time_scale.append(t_i)
        corr_data[:,:,:,frame_index] = corr



    corr_img = NibImg(img)
    corr_img.data = np.array(corr_data)

    return corr_img,out_time_scale


def decay_corr_dyn_img(img, time_scale, decay_factor=None):
    """
    Based on: 'Decay Correction Methods in Dynamic PET Studies - Kewei 1995' - Conventional decay correction technique 1.

    :param img:
    :param time_scale:
    :return:
    """

    if not isinstance(img, NibImg):
        img = read_image(img)

    if not isinstance(img,NibImg):
        raise TypeError

    if len(img.shape)!=4:
        printWarning("Input image is not 4 dimensional")
        raise TypeError

    if isinstance(decay_factor,type(None)):
        decay_factor = get_decay_factor()

    if img.shape[3]+1 != np.shape(time_scale)[0]:
        printWarning("Mismatch between image (len. of 4th dim + 1 = {0} ) and time scale (len = {1})".format(img.shape[3]+1,np.shape(time_scale)[0]))

    out_time_scale = []

    corr_data = np.zeros_like(img.data)

    for frame_index in range(img.shape[3]):
        t_1 = time_scale[frame_index]
        t_2 = time_scale[frame_index+1]

        t_i = (t_1+t_2)/2.0

        # pre_corr = img.data[:,:,:,time_index] / (t_2-t_1) #estimate middle of the frame...

        #frame middle estimation
        #function value approximation at t_i from integral of f(t) between t_1 and t_2
        est_factor_1 = 1.0

        pre_corr = img.data[:,:,:,frame_index] * est_factor_1

        factor = math.exp(decay_factor*t_i)
        # factor=1

        # print(factor)

        corr = pre_corr * factor


        out_time_scale.append(t_i)
        corr_data[:,:,:,frame_index] = corr



    corr_img = NibImg(img)
    corr_img.data = np.array(corr_data)

    return corr_img,out_time_scale

def decay_corr_avg_from_dyn_img(img, time_scale, decay_factor=None):
    """
    Based on: 'Decay Correction Methods in Dynamic PET Studies - Kewei 1995' - Conventional decay correction technique 1.

    :param img:
    :param time_scale:
    :return:
    """

    if not isinstance(img, NibImg):
        img = read_image(img)

    if not isinstance(img,NibImg):
        raise TypeError

    if len(img.shape)!=4:
        printWarning("Input image is not 4 dimensional")
        raise TypeError

    if isinstance(decay_factor,type(None)):
        decay_factor = get_decay_factor()

    if img.shape[3]+1 != np.shape(time_scale)[0]:
        printWarning("Mismatch between image (len. of 4th dim + 1 = {0} ) and time scale (len = {1})".format(img.shape[3]+1,np.shape(time_scale)[0]))

    out_time_scale = []

    corr_data = np.zeros_like(img.data)

    for frame_index in range(img.shape[3]):
        t_1 = time_scale[frame_index]
        t_2 = time_scale[frame_index+1]

        t_i = (t_1+t_2)/2.0

        # pre_corr = img.data[:,:,:,time_index] / (t_2-t_1) #estimate middle of the frame...

        #frame middle estimation
        #function value approximation at t_i from integral of f(t) between t_1 and t_2
        est_factor_1 = 1.0

        pre_corr = img.data[:,:,:,frame_index] * est_factor_1

        factor = math.exp(decay_factor*t_i)
        corr = pre_corr * factor

        out_time_scale.append(t_i)
        corr_data[:,:,:,frame_index] = corr



    corr_img = NibImg(img)
    corr_img.data = np.average(np.array(corr_data),axis=3)

    return corr_img,out_time_scale


def get_decay_factor(half_time = 109.77):
    return math.log(2)/(half_time*60.0)




if __name__ == '__main__':

    test_dyn_img = "/data/rabbit_dyn_pet/r001/pet/ic-r001_01-pet-6x10m_grappa.nii.gz"
    time_scale = np.arange(0,3600+600,600)

    decay_corr_img, frame_time_scale = decay_corr_signal_from_dyn_img(test_dyn_img,time_scale,get_decay_factor())

    decay_corr_img.save("/data/rabbit_dyn_pet/r001/pet/Dic-r001_01-pet-6x10m_grappa.nii.gz")

