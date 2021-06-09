#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Short explanation"""

import os, sys

sys.path.insert(0, '/home/fajtai/py/')
from Std_Tools.pet_processing.fdg_scaling import fdg_is_kBq
from Std_Tools.img_proc.IO.img_reader import read_image
from Std_Tools.data_mining.dcm_mining import dicom_extract_suv
from Common.colorPrint import *

test_dopa = "/home/fajtai/test/dcm/p004_01-pet-1.dcm1"
test_t1 = "/home/fajtai/test/dcm/t1_mpr_tra.dcm"

def get_bw_image(original_pet_path,dicom_path):
    if not os.path.exists(str(original_pet_path)):
        return
    if not os.path.exists(str(dicom_path)):
        return

    dicom_suv_data = dicom_extract_suv(dicom_path)

    if not dicom_suv_data:
        printWarning("Missing dcm file or suv information can not be extracted form dcm file '{0}'".format(dicom_path))
        return


    factor = dicom_suv_data.bw_factor/(dicom_suv_data.inj_dose * dicom_suv_data.f18_decay_factor)

    # if fdg_is_kBq(original_pet_path):
    #     factor = factor*1000

    I = read_image(original_pet_path)
    I.factor_scaling(factor)
    return I

def get_bsa_image(original_pet_path,dicom_path):
    if not os.path.exists(str(original_pet_path)):
        return
    if not os.path.exists(str(dicom_path)):
        return

    dicom_suv_data = dicom_extract_suv(dicom_path)

    if not dicom_suv_data:
        printWarning("Missing dcm file or suv information can not be extracted form dcm file '{0}'".format(dicom_path))
        return

    factor = dicom_suv_data.bsa_factor / (dicom_suv_data.inj_dose * dicom_suv_data.f18_decay_factor)

    # if fdg_is_kBq(original_pet_path):
    #     factor = factor*1000

    I = read_image(original_pet_path)
    I.factor_scaling(factor)
    return I

def get_lbm_image(original_pet_path,dicom_path):
    if not os.path.exists(str(original_pet_path)):
        return
    if not os.path.exists(str(dicom_path)):
        return

    dicom_suv_data = dicom_extract_suv(dicom_path)

    if not dicom_suv_data:
        printWarning("Missing dcm file or suv information can not be extracted form dcm file '{0}'".format(dicom_path))
        return

    factor = dicom_suv_data.lbm_factor / (dicom_suv_data.inj_dose * dicom_suv_data.f18_decay_factor)

    # if fdg_is_kBq(original_pet_path):
    #     factor = factor*1000

    I = read_image(original_pet_path)
    I.factor_scaling(factor)
    return I


def main():
    S = dicom_extract_suv(test_dopa)
    pass


if __name__ == '__main__':
    main()