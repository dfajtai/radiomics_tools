#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np
import scipy.ndimage as ndimage
import itertools

def check_coord(coord, shape):
    if any([coord[i] < 0 or coord[i] >= shape[i] for i in range(len(coord))]):
        return False
    return True

def neighbours_6(coord,shape,add_center = False,**kwargs):
    coords = [
        (coord[0]-1,coord[1],coord[2]),
        (coord[0]+1,coord[1],coord[2]),
        (coord[0],coord[1]-1,coord[2]),
        (coord[0],coord[1]+1,coord[2]),
        (coord[0],coord[1],coord[2]-1),
        (coord[0],coord[1],coord[2]+1),
    ]
    coords = filter(lambda x: check_coord(x,shape),coords)
    if add_center:
        coords.append(tuple(coord))

    return coords

def neighbours_6_mask(coord,shape,**kwargs):
    mask = np.zeros(shape)
    indices = neighbours_6(coord,shape,**kwargs)
    for i in indices:
        mask[i]=1
    return mask

def neighbours_3x3(coord,shape,add_center=False,**kwargs):
    I = range(max(0,coord[0]-1),min(shape[0],coord[0]+1)+1)
    J = range(max(0,coord[1]-1),min(shape[1],coord[1]+1)+1)
    K = range(max(0,coord[2]-1),min(shape[2],coord[2]+1)+1)

    coords = list(itertools.product(I,J,K))

    coords = filter(lambda x: check_coord(x, shape), coords)
    if add_center:
        coords.append(tuple(coord))

    return coords


def neighbours_3x3_mask(coord,shape,**kwargs):
    mask = np.zeros(shape)
    indices = neighbours_3x3(coord, shape,**kwargs)
    for i in indices:
        mask[i] = 1
    return mask


def neighbours_NxN(coord,shape,N,add_center = False,**kwargs):
    D = (N-1)/2

    I = range(max(0, coord[0] - D), min(shape[0], coord[0] + D) + 1)
    J = range(max(0, coord[1] - D), min(shape[1], coord[1] + D) + 1)
    K = range(max(0, coord[2] - D), min(shape[2], coord[2] + D) + 1)

    coords = list(itertools.product(I, J, K))

    coords = filter(lambda x: check_coord(x, shape), coords)
    if add_center:
        coords += [coord]

    return coords

