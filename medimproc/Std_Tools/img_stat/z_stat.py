#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import numpy as np

import matplotlib.pyplot as plt
from copy import copy

from Common.CommandRunner import CommandRunner

from Common.colorPrint import *

from Std_Tools import read_image
from Std_Tools import extendable_file as ex

import scipy.stats as stats
from statsmodels.stats import multitest as smm
from Std_Tools.img_stat.fdr_corr import p_fdr_corr_1, p_fdr_corr_2

def get_z_img(in_img_path,low_threshold=0.001):
    in_img_path = ex(in_img_path)
    if not in_img_path.exists():
        return
    I = read_image(in_img_path)
    I.threshold(low_threshold)

    ind = I.data>0
    mean = np.mean(I.data[ind])
    sd = np.std(I.data[ind])

    Z = lambda x: (x - mean)/sd
    Z_filter = np.vectorize(Z)
    I.data = Z_filter(I.data)

    return I


def z_from_dist(sample_ndarray,ref_dist,sample_mask=None):
    if not isinstance(sample_ndarray,np.ndarray):
        return
    if not isinstance(ref_dist, np.ndarray):
        return
    ref_dist = ref_dist.flatten()

    mean = np.mean(ref_dist)
    sd = np.std(ref_dist)
    Z = lambda x: (x - mean) / sd
    Z_filter = np.vectorize(Z)

    if isinstance(sample_mask,np.ndarray):
        indices = np.argwhere(sample_mask > 0)
        Z_data = np.zeros_like(sample_ndarray)
        for i in indices:
            Z_data[tuple(i)] = Z(sample_ndarray[tuple(i)])
    else:

        return Z_filter(sample_ndarray)

def z_from_dist_params(sample_ndarray, ref_dist_mean, ref_dist_sd, sample_mask=None):
    if not isinstance(sample_ndarray,np.ndarray):
        return

    Z = lambda x: (x - ref_dist_mean) / ref_dist_sd
    Z_filter = np.vectorize(Z)

    if isinstance(sample_mask,np.ndarray):
        indices = np.argwhere(sample_mask > 0)
        Z_data = np.zeros_like(sample_ndarray)
        for i in indices:
            Z_data[tuple(i)] = Z(sample_ndarray[tuple(i)])
        return Z_data

    else:
        return Z_filter(sample_ndarray)

def z_from_dist_p(sample_ndarray,ref_dist,sample_mask=None, fdr_corr = False, target_fdr = 0.05):
    if not isinstance(sample_ndarray,np.ndarray):
        return
    if not isinstance(ref_dist, np.ndarray):
        return
    ref_dist = ref_dist.flatten()

    mean = np.mean(ref_dist)
    sd = np.std(ref_dist)
    Z_p = lambda x: stats.norm.cdf((x - mean) / sd)
    Z_p_filter = np.vectorize(Z_p)

    if isinstance(sample_mask,np.ndarray):
        indices = np.argwhere(sample_mask > 0)
        Z_p_data = np.zeros_like(sample_ndarray)
        for i in indices:
            Z_p_data[tuple(i)] = Z_p(sample_ndarray[tuple(i)])
    else:

        Z_p_data = Z_p_filter(sample_ndarray)

    if fdr_corr:
        Z_p_data = p_fdr_corr_1(Z_p_data,target_fdr)

    return Z_p_data

def convert_z_2_p(Z_array):
    Z_p = lambda x: stats.norm.cdf(x)
    Z_p_filter = np.vectorize(Z_p)
    Z_p_data = Z_p_filter(Z_array)
    return Z_p_data


def z_critical_one_tail(p=0.001):
    return stats.norm.ppf(p)


def fdr_z_crit(z_map,target_alpha=0.05):
    p_uncorr = convert_z_2_p(z_map)
    p_corr, reject_fdr = p_fdr_corr_2(p_uncorr,target_alpha)
    threshold_fdr = np.min(np.abs(z_map)[reject_fdr])

    return threshold_fdr