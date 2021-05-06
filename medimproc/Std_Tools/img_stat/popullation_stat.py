#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import numpy as np
from copy import copy
from scipy import stats

from Common.CommandRunner import CommandRunner
from Common.colorPrint import *
from Std_Tools import read_image
from Std_Tools import extendable_file as ex

def pop_reader(img_list):
    pop_data = []
    I = None
    for i in img_list:
        if not ex(i).exists:
            continue
        try:
            I = read_image(i)
            pop_data.append(I.data)

        except:
            pass


    return pop_data, I

def pop_mean(img_list):
    pop_data,sample_img = pop_reader(img_list)
    try:
        mean = np.mean(pop_data,axis=0)
        sample_img.data = mean
        return sample_img

    except:
        printError("Error during computing population mean image...")

def pop_std(img_list):
    pop_data,sample_img = pop_reader(img_list)
    try:
        sd = np.std(pop_data,axis=0)
        sample_img.data = sd
        return sample_img

    except:
        printError("Error during computing population std image...")


def pop_cv(img_list):
    pop_data, sample_img = pop_reader(img_list)
    try:
        mean = np.mean(pop_data, axis=0)
        sd = np.std(pop_data,axis=0)
        sample_img.data = np.divide(sd,mean)
        return sample_img

    except:
        printError("Error during computing population cv image...")



