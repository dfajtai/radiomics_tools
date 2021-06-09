#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Short explanation"""

import os, sys
import numpy as np
import copy
import math

sys.path.insert(0, '/home/fajtai/py/')

def get_affine_origin(affine):
    return affine[0:3, 3]

def set_affine_origin(affine,new_origin):
    _affine = copy.copy(affine)
    n = new_origin[:]
    for i in range(3):
        _affine[i, 3] = n[i]
    return _affine

def translate_affine(affine,translation_vector):
    a = get_affine_origin(affine)
    a = np.array(a) + np.array(translation_vector)
    return a

def get_step_sizes(affine,correct_negative_step= True):
    _affine =affine[0:3, 0:3]

    def correctSizes(affine):
        signs = np.sign(affine)
        signs[signs==0] = 1
        return np.prod(signs,axis=0)

    sizes =np.linalg.norm(_affine,axis=0)

    if correct_negative_step:
        sizes = sizes * correctSizes(_affine)

    return sizes


def voxel_2_world(voxel_coord, affine, ignore_negative_step = False):
    voxel_coord = np.array(voxel_coord[:])
    if ignore_negative_step:
        step = np.abs(get_step_sizes(affine))
    else:
        step = get_step_sizes(affine)

    return tuple(np.array(get_affine_origin(affine)) + (voxel_coord * step))


def world_2_voxel(world_coord, affine,  toIndex = True, ignore_negative_step = False, abs_negative_voxel_coord=True):
    world_coord = np.array(world_coord[:])
    sizes = get_step_sizes(affine)
    if ignore_negative_step:
        sizes=np.abs(sizes)
    start = get_affine_origin(affine)

    voxel_coord = np.array(world_coord-start)
    voxel_coord = voxel_coord / sizes

    if abs_negative_voxel_coord:
        voxel_coord = np.abs(voxel_coord)

    if toIndex:
        return tuple(voxel_coord.astype("int"))
    else:
        return tuple(voxel_coord)

def correct_vox_coord(voxel_coord,max_size):
    P = []
    for m,p in zip(max_size,voxel_coord):
        _p = min(m,p) if p>0 else 0
        P.append(_p)
    return tuple(P)


def factor_rescale_affine(affine, factor):
    if not isinstance(affine, np.ndarray):
        return affine

    if affine.shape != (4,4):
        return affine

    for i in range(0,4):
        affine[0:3,i]=affine[0:3,i]*factor

    return affine

def get_abs_step_sizes(affine):
    step = np.power(np.sum(np.square(affine[:,:3]),axis=0),0.5)

    return step

def get_start(affine,offset=None):
    if isinstance(offset,np.array):
        return affine[:-1,-1] + offset
    else:
        return affine[:-1,-1]

def get_rot_matrix(affine):
    step = get_abs_step_sizes(affine)
    rotM = np.divide(affine[:3,:3],step)

    return rotM

def get_rot_values(affine):
    rotM = get_rot_matrix(affine)
    rotx = math.atan2(rotM[2, 1], rotM[2, 2]) * (180 / math.pi)
    roty = math.atan2(-rotM[2, 0], math.sqrt(np.sum([np.square(rotM[2, 1]), np.square(rotM[2, 2])]))) * (180 / math.pi)
    rotz = math.atan2(rotM[0, 1], rotM[0, 0]) * (180 / math.pi)

    return rotx,roty,rotz

def main():
    pass


if __name__ == '__main__':
    main()