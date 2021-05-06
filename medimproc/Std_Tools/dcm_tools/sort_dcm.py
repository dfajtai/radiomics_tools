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


# from types import NoneType
NoneType = type(None)

#todo sort list of dicom files to multiple list by key values (eg.: series instance uid, series decripition, etc) then save each list to a folder named with the examined key value

def get_firtst_dcm_file(dcm_dir):
    if not os.path.exists(dcm_dir):
        return

    files =[os.path.join(dcm_dir,f) for f in os.listdir(dcm_dir)]

    dcm_files = []

    for f in files:
        try:
            dcm = dicom.read_file(f)
            dcm_files.append(f)
            break

        except InvalidDicomError as e:
            continue

    return dcm_files[0]

def get_dcm_series_number(dcm_dir):
    if not os.path.exists(dcm_dir):
        return

    files =[os.path.join(dcm_dir,f) for f in os.listdir(dcm_dir)]

    dcm_files = []
    dcm_accession_number=[]
    i=0
    files = random.sample(files,1000)

    for f in files:
        try:
            dcm = dicom.read_file(f)
            dcm_files.append(f)

            dcm_accession_number.append(dcm.SeriesNumber)
            i+=1
            print(i)
            # break

        except InvalidDicomError as e:
            continue

    return dcm_files,dcm_accession_number


def sort_by_series_number(dcm_dir,out_dir):
    if not os.path.isdir(dcm_dir):
        return

    f,an = get_dcm_series_number(dcm_dir)
    pass

if __name__ == '__main__':
    dcm_dir = "/data/dicom/rabbit/20.5.N.003/20200117-1507-PTMR/new/20.5.N.003/dcm"
    sort_by_series_number(dcm_dir,"")
    pass