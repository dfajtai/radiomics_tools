#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np


sys.path.insert(0, '/home/fajtai/py/')


def _get_neighbouring_voxels(pt, checked, dims):
    """

    :param pt: i,j,k coordinate
    :param checked: checked matrix
    :param dims: matrix dimension
    :return:
    """
    nbhd = []  # neighbourhood

    if (pt[0] > 0) and not checked[pt[0] - 1, pt[1], pt[2]]:
        nbhd.append((pt[0] - 1, pt[1], pt[2]))

    if (pt[1] > 0) and not checked[pt[0], pt[1] - 1, pt[2]]:
        nbhd.append((pt[0], pt[1] - 1, pt[2]))

    if (pt[2] > 0) and not checked[pt[0], pt[1], pt[2] - 1]:
        nbhd.append((pt[0], pt[1], pt[2] - 1))

    if (pt[0] < dims[0] - 1) and not checked[pt[0] + 1, pt[1], pt[2]]:
        nbhd.append((pt[0] + 1, pt[1], pt[2]))

    if (pt[1] < dims[1] - 1) and not checked[pt[0], pt[1] + 1, pt[2]]:
        nbhd.append((pt[0], pt[1] + 1, pt[2]))

    if (pt[2] < dims[2] - 1) and not checked[pt[0], pt[1], pt[2] + 1]:
        nbhd.append((pt[0], pt[1], pt[2] + 1))

    return nbhd

def growth(data, start_point, radius):
    """
    Simple region growing algorithm

    :param data: data matrix
    :type data: numpy.ndarray

    :param start_point: i,j,k starting coordinate
    :type start_point: tuple

    :param radius: radius of the kernel

    :return: growth region
    """

    seg = np.zeros(data.shape, dtype=np.bool)
    checked = np.zeros_like(seg)

    seg[start_point] = True
    checked[start_point] = True

    shape = data.shape

    needs_check = _get_neighbouring_voxels(start_point,checked, shape)

    while len(needs_check)>0:
        pt = needs_check.pop()

        if checked[pt]:continue

        checked[pt] = True

        imin = max(pt[0]-radius,0)
        imax = min(pt[0]+radius,shape[0]-1)
        jmin = max(pt[1] - radius, 0)
        jmax = min(pt[1] + radius, shape[1] - 1)
        kmin = max(pt[2] - radius, 0)
        kmax = min(pt[2] + radius, shape[2] - 1)

        #kritérium...

        if data[pt] >= data[imin:imax+1, jmin+jmax+1, kmin:kmax+1].mean():
            seg[pt]= True
            needs_check+=_get_neighbouring_voxels(pt,checked,data.shape)

    return seg #:type numpy.ndarray

def main():
    pass
    # growth()


if __name__ == '__main__':
    main()