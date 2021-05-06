#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backward compatibility code
"""
import sys
import numpy as np
import itertools

sys.path.insert(0, '/home/fajtai/py/')
from Std_Tools.img_proc.IO.img_reader import read_image, NibImg
from Std_Tools.img_proc.bounding_box_functions import *

def box_crop_fix(I,p1w,p2w, target_origin=None):
    if not isinstance(I,NibImg):
        try:
            _I = read_image(I)
            if not isinstance(_I,NibImg):
                return
            I = _I
        except Exception as e:
            return e

    I.box_crop_world(p1w,p2w,target_origin=target_origin,inplace=True)

    return I


def box_crop_fix_voxel(img_path,p1,p2):
    I = read_image(img_path)
    I.box_crop_voxel(p1,p2,inplace=True)

    return I


def box_crop_relative(img_path,p1w,vox_count, target_origin=None):
    I = read_image(img_path)
    I.box_crop_world_rel(p1w,vox_count,target_origin=target_origin,inplace=True)

    return I