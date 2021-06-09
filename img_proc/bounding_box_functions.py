#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import numpy as np
import itertools

sys.path.insert(0, '/home/fajtai/py/')

def bbox_3d(data):
    x = np.any(data, axis=(1, 2))
    y = np.any(data, axis=(0, 2))
    z = np.any(data, axis=(0, 1))

    xmin, xmax = np.where(x)[0][[0, -1]]
    ymin, ymax = np.where(y)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]

    return xmin, xmax, ymin, ymax, zmin, zmax

def bbox_Nd(data):
    N = data.ndim
    out = []
    for ax in itertools.combinations(range(N), N - 1):
        nonzero = np.any(data, axis=ax)
        out.extend(np.where(nonzero)[0][[0, -1]])
    return tuple(out)

def first_last_in_axis(data,axis,threshold=0):
    """
    :param data: np.array which stores image information
    :param axis: 0,1,2
    :type axis: int
    :param threshold: threshold value, acts as a high-pass filter
    :return: first and last nonzero index in the given direction
    """

    indices = list(np.argwhere(data>threshold))
    indices.sort(key=lambda x:x[axis])
    return indices[0], indices[-1]


def bbox_3d_with_iso_border(data, border):
    b_x, b_y, b_z = data.shape
    xmin,xmax,ymin,ymax,zmin,zmax = bbox_3d(data)


    xmin = max(0,xmin-border)
    ymin = max(0,ymin-border)
    zmin = max(0,zmin-border)

    xmax = min(b_x,xmax+border)
    ymax = min(b_y,ymax+border)
    zmax = min(b_z,zmax+border)

    return (xmin, ymin, zmin),  (xmax,  ymax,  zmax)

def bbox_with_3_border(data,x=0,y=0,z=0):
    b_x, b_y, b_z = data.shape
    xmin, xmax, ymin, ymax, zmin, zmax = bbox_3d(data)
    xmin = max(0, xmin - x)
    ymin = max(0, ymin - y)
    zmin = max(0, zmin - z)

    xmax = min(b_x, xmax + x)
    ymax = min(b_y, ymax + y)
    zmax = min(b_z, zmax + z)

    return (xmin, ymin, zmin), (xmax, ymax, zmax)
