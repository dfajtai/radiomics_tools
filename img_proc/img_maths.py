#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from optparse import OptionParser
import numpy as np
import math
from scipy import stats as stats
import scipy.ndimage as ndimage
import numpy.linalg as alg
from ImgProc.basics import *

def symm_corr(data,axis="x",pre_mask= None):
    if axis not in ["x","y","z"]:
        return
    if not isinstance(data,np.ndarray):
        return

    if isinstance(pre_mask,np.ndarray):
        data = data*pre_mask

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






symm_corr("","x")