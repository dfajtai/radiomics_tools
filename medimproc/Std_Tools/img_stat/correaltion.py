#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import numpy as np
from copy import copy
from scipy import stats
import math

from Std_Tools.img_proc.neighbours import neighbours_3x3


def mirror(data,x=False,y=False,z=False):
    if x: data = data[::-1,:,:]
    if y: data = data[:,::-1,:]
    if z: data = data[:,:,::-1]

    return data

def symm_corr(data,axis="x",pre_mask= None):
    if axis not in ["x","y","z"]:
        return
    if not isinstance(data,np.ndarray):
        return

    if isinstance(pre_mask,np.ndarray):

        if data.shape == pre_mask.shape:
            data[pre_mask<=0]=0

    axes = {"x":0,"y":1,"z":2}
    params = axes.copy()
    for k in params.keys(): params[k] = True if k == axis else False

    mirrored_data = mirror(data,**params)

    dim_len = data.shape[axes[axis]]
    L = int(math.floor(dim_len/2.0))

    if axis == "x":
        data_half = data[0:L,:,:]
        m_data_half = mirrored_data[0:L,:,:]
    elif axis == "y":
        data_half = data[:,0:L,:]
        m_data_half = mirrored_data[:,0:L,:]
    else:
        data_half = data[:,:,0:L]
        m_data_half = mirrored_data[:,:,0:L]

    d = data_half.flatten()
    d_m = m_data_half.flatten()
    return np.corrcoef(d,d_m)[1,0]


def corr_data_N27(sampe_data,reference_data,domain):
    if not isinstance(reference_data, np.ndarray):
        return
    if not isinstance(sampe_data,np.ndarray):
        return
    if not isinstance(domain,np.ndarray):
        return

    if not domain.shape == reference_data.shape == sampe_data.shape:
        return

    def vox_corr(x,ref):
        corr_coeff = np.corrcoef(x,ref)[1,0]
        return corr_coeff


    if np.sum(domain) == 0:
        return np.zeros_like(domain)

    t_stat_data = np.zeros_like(domain).astype("float64")
    indices = np.argwhere(domain>0)

    for i in indices:
        ind = neighbours_3x3(i,domain.shape,add_center=True)
        ref = np.array([reference_data[n] for n in ind])
        samp = np.array([sampe_data[n] for n in ind])
        t_stat_data[tuple(i)]=vox_corr(samp,ref)

    return t_stat_data