#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys

import numpy as np
import math
import scipy.ndimage as ndimage

def generate_kernel(shape = 1):
    #1 for diamond
    K = ndimage.generate_binary_structure(3,shape).astype(int)
    return K

def generate_spherical_kernel(radius = 5):
    return spherical_kernel(N=radius)

def spherical_kernel(N, center=None, R=None, mask_val=1):
    if R is None:
        R = math.floor(N / 2.0)
        # print(R)
    if center is None:
        center = [math.floor(N / 2.0)] * 3
        # print(center)
    Z, Y, X = np.ogrid[-center[0]:N - center[0], -center[1]:N - center[1], -center[2]:N - center[2]]
    mask = X * X + Y * Y + Z * Z <= R * R

    array = np.zeros((N, N, N))
    array[mask] = mask_val

    return array