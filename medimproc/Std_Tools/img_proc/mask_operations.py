#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np
from numpy import linalg
import pandas as pd
from scipy.spatial.distance import dice, directed_hausdorff
import itertools

NoneType = type(None)

import scipy.ndimage
from scipy.ndimage import morphology
import skimage as ski
from skimage.morphology import ball, cube, octahedron

def mask_splitter_by_distance(mask_data,point_name_dict):
    """
    :param mask_data: np.array which contains a binary mask that you want to split in pieces
    :param point_name_dict: dictionary, with named points. eg.: {"center":(0,0,0)}
    :return: dictionary of names and nd.arrays
    """
    if not isinstance(mask_data,np.ndarray):
        raise TypeError
    if not isinstance(point_name_dict,dict):
        raise TypeError

    dim_count = len(mask_data.shape)
    valid_names = [n for n in point_name_dict.keys() if len(point_name_dict[n])==dim_count]
    points = [np.array(point_name_dict[n]) for n in valid_names]

    splitted_mask = np.zeros_like(mask_data)

    mask_indices = np.argwhere(mask_data==1)
    for i in mask_indices:
        distances = [linalg.norm(i-p) for p in points]
        min_index = np.argmin(distances)
        splitted_mask[i[0],i[1],i[2]] =min_index+1

    split_mask_dict= {}

    for i, name in zip(range(len(valid_names)),valid_names):
        split_mask_dict[name] = (splitted_mask == i+1).astype("int")

    return split_mask_dict


def mask_filter_distance_less(mask_data,center,distance):
    if not isinstance(mask_data,np.ndarray):
        raise TypeError
    filtered_mask = np.zeros_like(mask_data)
    mask_indices = np.argwhere(mask_data == 1)
    for i in mask_indices:
        d = linalg.norm(i-center)
        if d < distance:
            filtered_mask[i[0],i[1],i[2]] = 1
    return filtered_mask


def mask_matching_measurement(dict_of_masks):
    """
    compares each pair of binary masks - stored in ndarrays
    :param dict_of_masks: dictionary of ndarrays
    :return: dataframe
    """

    df = pd.DataFrame()
    if not isinstance(dict_of_masks,dict):
        return df

    for comb in itertools.combinations(dict_of_masks.keys(),2):
        A = dict_of_masks[comb[0]]
        B = dict_of_masks[comb[1]]
        if not (isinstance(A,np.ndarray) and isinstance(B,np.ndarray)):
            row = {"mask.1":comb[0],"mask.2":comb[1],"dice":np.nan,
               "hausdorff":np.nan,"vol.1":np.nan,"vol.2":np.nan,"overlap":np.nan}
            df = df.append(row,ignore_index = True)
            continue


        A = A.astype(np.bool)
        B = B.astype(np.bool)

        if np.sum(A)==0 or np.sum(B)==0:
            row = {"mask.1":comb[0],"mask.2":comb[1],"dice":np.nan,
               "hausdorff":np.nan,"vol.1":np.sum(A),"vol.2":np.sum(B),"overlap":np.nan}
            df = df.append(row,ignore_index = True)
            continue

        A_ind = np.argwhere(A==1)
        B_ind = np.argwhere(B==1)

        D = 2.0*(np.sum(A[B==1]))/(np.sum(A)+np.sum(B))

        row = {"mask.1":comb[0],"mask.2":comb[1],"dice":D,
               "hausdorff":directed_hausdorff(A_ind,B_ind),"vol.1":np.sum(A),"vol.2":np.sum(B),"overlap":np.sum(A[B==1])}

        df = df.append(row,ignore_index = True)

    return df


def convex_hull_by_morph(initial_mask, increase_radius = 10, decrease_radius = 2, surface_growth_limit = 0, increase_func = None, decrease_func = None ):
    iter_limit = 20

    dilation_kernel = ball(increase_radius)
    erosion_kernel = ball(decrease_radius)

    if isinstance(increase_func,NoneType):
        increase_func = morphology.binary_dilation

    if isinstance(decrease_func,NoneType):
        decrease_func = morphology.binary_erosion

    surface_kernel = morphology.generate_binary_structure(3, 3)

    def __surface_voxel_count__(m, kernel):
        _m = decrease_func(m, structure=kernel, iterations=1)
        return np.sum(m) - np.sum(_m)

    mask = increase_func(initial_mask, dilation_kernel, iterations=1)
    surface = __surface_voxel_count__(mask, surface_kernel)

    i = 0
    surface_growth_count = 0
    while True:
        if i > iter_limit:
            raise OverflowError("iteration limit reached")

        _mask = np.logical_or(decrease_func(mask, erosion_kernel, iterations=1), initial_mask)
        _surface = __surface_voxel_count__(_mask, surface_kernel)

        change = _surface - surface
        ratio = abs(float(change) / float(surface)) if surface != 0 else 0

        # print(change, ratio)

        if change>0:
            surface_growth_count +=1
        else:
            surface_growth_count = 0

        if change == 0:
            break

        if surface_growth_count > surface_growth_limit:
            break
        else:
            mask = _mask
            surface = _surface
            i += 1

    return mask, surface
