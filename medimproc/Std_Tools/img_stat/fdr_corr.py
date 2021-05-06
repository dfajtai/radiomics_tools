#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import numpy as np

import matplotlib.pyplot as plt


from Std_Tools import read_image
from Std_Tools import extendable_file as ex

import scipy.stats as stats
from statsmodels.stats import multitest as smm
from mne.stats import bonferroni_correction, fdr_correction


def __hist_plot(sample):
    n, bins, patches = plt.hist(sample, 30, facecolor='g', alpha=0.75)
    plt.grid(True)
    plt.show()

def p_fdr_corr_1(p_map,highpass = -1, alpha = 0.001):
    """
    :param p_map: ndarray, contains p values
    :param alpha: target significance level
    :return: corrected array of p values
    """

    #flatten
    shape = p_map.shape
    p_flatten = p_map.flatten()

    #get elements abowe threshold...
    p_filtered_indices = np.argwhere(p_flatten>highpass)
    p_filtered = p_flatten[p_filtered_indices].reshape(len(p_filtered_indices))

    #save order to restore original order
    orig_index = np.argsort(p_filtered)
    sorted_p = p_filtered[orig_index]

    # __hist_plot(sorted_p)


    _,corr_p = smm.multipletests(sorted_p, alpha= alpha, method="fdr_i",is_sorted=True)[:2]
    # __hist_plot(corr_p)

    #undo sorting
    corr_p = zip(orig_index,corr_p)
    corr_p.sort(key= lambda x:x[0])
    corr_p = [j for i,j  in corr_p]
    # __hist_plot(corr_p)


    #undo masking
    corr_p_map = np.zeros_like(p_flatten)
    for i in range(len(p_filtered_indices)):
        corr_p_map[p_filtered_indices[i]]=corr_p[i]

    #reshaping
    corr_p_map = np.array(corr_p_map).reshape(shape)
    return corr_p_map


def p_fdr_corr_2(p_map, alpha = 0.05):
    """
    :param p_map: ndarray, contains p values
    :param alpha: target significance level
    :return: corrected array of p values
    """

    #__hist_plot(p_flatten)
    # _,corr_p = smm.multipletests(sorted_p, alpha= alpha, method="hommel", is_sorted= True)[:2]
    reject,corr_p = fdr_correction(p_map, alpha= alpha)[:2]
    #__hist_plot(corr_p)

    return corr_p,reject

