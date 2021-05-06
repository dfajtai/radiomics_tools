#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import pandas as pd
import re
import numpy as np
import random

import pydicom as dicom
from pydicom.errors import InvalidDicomError

from Std_Tools.common.py_io import *
from Std_Tools import extendable_file as ex


def sort_dcm_for_map07(target_dir,out_dir):
    accepted_sd = ['Head_t2_space_dark-fluid_sag_p2_iso','Head_t2_space_sag_p2_iso','Head_t1_mprage_sag_p2_iso']
    files = [os.path.join(target_dir,p) for p in os.listdir(target_dir)]
    for f in files:
        D = dicom.read_file(f)
        out_path = os.path.join(out_dir,D.StudyInstanceUID,D.SeriesInstanceUID)

        try:
            sd = D.SeriesDescription

            if sd not in accepted_sd:
                continue

            if not os.path.isdir(out_path):
                py_mkdirs(out_path)
            py_copy(f, os.path.join(out_path, os.path.basename(f)))
        except:
            continue


def check_sd(target_dir):
    subdirs = os.listdir(target_dir)
    for sd in subdirs:
        if not os.path.isdir(os.path.join(target_dir,sd)):
            continue
        files = os.listdir(os.path.join(target_dir,sd))

        f = files[0]
        p = os.path.join(target_dir,sd,f)
        d = dicom.read_file(p)
        try:
            print("'{0}' : '{1}'".format(d.SeriesDescription, d.ProtocolName))
        except:
            continue


def main():
    target_dir = "/data/map07/dcm/PTMR001848/dcm/"
    out_dir = "/data/map07/dcm/"
    sort_dcm_for_map07(target_dir,out_dir)
    check_sd("/data/map07/dcm/1.2.826.0.1.3680043.2.93.2.168435457.48043.1580724744.1")

if __name__ == '__main__':
    main()