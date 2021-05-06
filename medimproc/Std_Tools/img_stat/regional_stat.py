#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import numpy as np
from copy import copy
from scipy import stats
from scipy.stats import shapiro


from Common.CommandRunner import CommandRunner
from Common.colorPrint import *
from Std_Tools import read_image
from Std_Tools.img_proc.IO.img_reader import NibImg
from Std_Tools import extendable_file as ex


def __stat_map(sample_img, label_img, function):
    if not hasattr(function,"__call__"):
        printError("Error! Parameter named 'function' must be a function!")

    if not isinstance(sample_img,NibImg):
        try:
            sample_img_path = sample_img
            sample_img = read_image(str(sample_img_path))

        except:
            printError("Error during opening image {0}".format(str(sample_img_path)))
            return

    if not isinstance(label_img,NibImg):
        try:
            label_img_path = label_img
            label_img = read_image(str(label_img_path))

        except:
            printError("Error during opening image {0}".format(str(label_img_path)))
            return


    labels = np.unique(label_img.data)
    labels.sort()
    labels = labels[labels!=0]

    M = np.zeros_like(label_img.data)
    for l in labels:
        ind = label_img.data == l
        M[ind] = function(sample_img.data[ind])

    M_img = sample_img.c()
    M_img.data = M

    return M_img

def __stat_table(sample_img, label_img, region_df, function):
    if not hasattr(function,"__call__"):
        printError("Error! Parameter named 'function' must be a function!")

    if not isinstance(sample_img,NibImg):
        try:
            sample_img_path = sample_img
            sample_img = read_image(str(sample_img_path))

        except:
            printError("Error during opening image {0}".format(str(sample_img_path)))
            return

    if not isinstance(label_img,NibImg):
        try:
            label_img_path = label_img
            label_img = read_image(str(label_img_path))

        except:
            printError("Error during opening image {0}".format(str(label_img_path)))
            return


    labels = list(set(region_df["i"][:]))
    M_df = copy(region_df)
    M_df["{0}".format(function.__name__)]= None

    for l in labels:
        ind = label_img.data == l
        # print(M_df[M_df["i"]==l])
        value = function(sample_img.data[ind])
        M_df.at[M_df["i"]==l,"{0}".format(function.__name__)]= value

    return M_df


def mean_map(sample_img, label_img):
    return __stat_map(sample_img = sample_img, label_img = label_img, function= np.mean)

def mean_stat_table(sample_img, label_img, region_df):
    return __stat_table(sample_img=sample_img, label_img=label_img, region_df = region_df, function=np.mean)

def std_map(sample_img, label_img):
    return __stat_map(sample_img = sample_img, label_img = label_img, function= np.std)

def std_stat_table(sample_img, label_img, region_df):
    return __stat_table(sample_img=sample_img, label_img=label_img, region_df = region_df, function=np.std)

def cv_map(sample_img, label_img):
    def cv(ndarray):
        return np.std(ndarray) / np.mean(ndarray)
    return __stat_map(sample_img = sample_img, label_img = label_img, function= cv)

def cv_stat_table(sample_img, label_img, region_df):
    def cv(ndarray):
        return np.std(ndarray)/np.mean(ndarray)
    return __stat_table(sample_img=sample_img, label_img=label_img, region_df = region_df, function=cv)

def normality_map(sample_img, label_img):
    def normality(ndarray):
        try:
            stat, p = shapiro(ndarray)
            return p
        except:
            return 1

    return __stat_map(sample_img = sample_img, label_img = label_img, function= normality)

def normality_table(sample_img, label_img, region_df):
    def normality(ndarray):
        try:
            stat, p = shapiro(ndarray)
            return p
        except:
            return 1

    return __stat_table(sample_img=sample_img, label_img=label_img, region_df = region_df, function=normality)