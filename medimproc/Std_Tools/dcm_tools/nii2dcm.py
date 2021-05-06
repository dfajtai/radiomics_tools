#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os,sys
import time
import datetime
import copy

import pydicom as dicom
from pydicom import uid

from pydicom.errors import InvalidDicomError
import SimpleITK as sitk

import numpy as np
from Std_Tools import NibImg, read_image
from Std_Tools.img_proc.IO.affine_handler import get_abs_step_sizes, get_start, get_rot_matrix
from Std_Tools.common.py_io import py_remove
from Std_Tools.common import CommandRunner

import pandas as pd

def get_dcm_files(dcm_dir):
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

    return dcm_files



def nii_2_dcm_int(orig_nii, sample_dcm, out_path, series_description= None, remove_private =True):
    I = read_image(orig_nii, negative_step_correction=True)

    step = get_abs_step_sizes(I.affine)
    rot_matrix = get_rot_matrix(I.affine)
    slice_rot_vector = rot_matrix[:, :2].T.flatten().tolist()

    #
    dcm = dicom.read_file(sample_dcm)

    if remove_private:
        try:
            dcm.remove_private_tags()
        except:
            pass

    # image position patient (IPP)
    IPP = np.array(I.affine_origin)

    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    now_time_str = datetime.datetime.now().strftime("%Y%m%d")
    now_date_str = datetime.datetime.now().strftime("%H%M%S%f")

    # generating new SOPI UID
    orig_sopi_uid = dcm.SOPInstanceUID
    orig_sopi_uid_start = orig_sopi_uid.rsplit(".", 1)[0]
    new_sopi_uid_time_full = now_str + orig_sopi_uid.rsplit(".", 1)[1][-5:]
    new_sopi_uid_time = str(new_sopi_uid_time_full)[:-5]
    new_sopi_uid_index = int(str(new_sopi_uid_time_full)[-5:])  # increment by slice

    # generating new series instance uid
    study_instance_uid = dcm.SeriesInstanceUID
    if len(study_instance_uid) == 58:
        new_study_instance_uid = study_instance_uid.rsplit(".", 4)[0] + "." + now_str + study_instance_uid.rsplit(".", 4)[1][-5:] + ".0.0.0"
    else:
        new_study_instance_uid = study_instance_uid.rsplit(".", 1)[0] + "." + now_str + study_instance_uid.rsplit(".", 1)[1][-5:]
    dcm.SeriesInstanceUID = new_study_instance_uid

    # set data type prop
    DATA = np.array(I.data).astype(np.uint16)
    # dcm.PixelData = dcm.pixel_array.astype(dtype)

    type_max = np.iinfo(dcm.pixel_array.dtype).max
    data_max = np.max(I.data)

    # slope=type_max/data_max
    slope = 1

    # create copy

    slice_prototype = copy.deepcopy(dcm)
    slice_prototype.SOPClassUID = dcm.file_meta.MediaStorageSOPClassUID
    slice_prototype.SecondaryCaptureDeviceManufacturer = "Medicopus"
    if isinstance(series_description, type(None)):
        slice_prototype.SeriesDescription = str(dcm.SeriesDescription) + "_post_proc"
    else:
        slice_prototype.SeriesDescription = series_description

    #set time


    #set value representation
    slice_prototype.SamplesPerPixel = 1
    slice_prototype.PhotometricInterpretation = "MONOCHROME2"
    slice_prototype.PixelRepresentation = 0
    slice_prototype.HighBit = 11
    slice_prototype.BitsStored = 16
    slice_prototype.BitsAllocated = 16

    # slice_prototype.RescaleSlope = slope
    # slice_prototype.RescaleIntercept = -1024
    slice_prototype.RescaleSlope = None
    slice_prototype.RescaleIntercept = None

    #set spatial prop

    slice_prototype.PixelSpacing = step[:2].tolist()
    slice_prototype.ImageOrientation = slice_rot_vector
    # slice_prototype.ImageOrientationPatient = [1, 0, 0, 0, 0, -1, 0]
    slice_prototype.ImageOrientationPatient = [1, 0, 0, 0, 1, 0,]

    slice_prototype.Columns = DATA.shape[0]
    slice_prototype.Rows = DATA.shape[1]

    # indexing properties
    start_position = IPP
    start_instance_number = 1  # instance number

    for slice_index in np.arange(0, DATA.shape[2]):
        img_slice = copy.deepcopy(slice_prototype)
        # indexing
        img_slice.SOPInstanceUID = "{orig}.{time}{index}".format(orig=orig_sopi_uid_start, time=new_sopi_uid_time, index=str(int(new_sopi_uid_index + slice_index)))

        instance_number = start_instance_number + slice_index
        img_slice.InstanceNumber = instance_number

        # updating position
        # slice_patient_position = (start_position + (rot_matrix[:3, 2] * slice_index * step[2])).tolist()
        slice_patient_position = (start_position + (np.array([0, 0, step[2]])*slice_index)).tolist()
        slice_location = start_position[2] + (slice_index * step[2])

        img_slice.ImagePositionPatient = slice_patient_position

        img_slice.SliceLocation = slice_location

        # slice
        SLICE_DATA = DATA[::-1, :, slice_index]
        SLICE_DATA = SLICE_DATA.astype(np.uint16)
        img_slice.PixelData = np.rot90(SLICE_DATA).tostring()

        # file_name
        out_filename = os.path.join(out_path, img_slice.SOPInstanceUID)


        img_slice.save_as(out_filename)




if __name__ == '__main__':
    sample_dicom_dir  = "/home/fajtai/py/Std_Tools/dcm_tools/test/t1_fl2d_fs_cor"
    sample_nii = "/home/fajtai/py/Std_Tools/dcm_tools/test/t1_fl2d_fs_cor/t1_fl2d_fs_cor_t1_fl2d_fs_cor_20200117133350_64.nii"
    sample_nii = "/home/fajtai/py/Std_Tools/dcm_tools/test/sample.nii"


    out_path = "/home/fajtai/py/Std_Tools/dcm_tools/test/out_dcm"

    py_remove([os.path.join(out_path,f) for f in os.listdir(out_path)])

    # nii_2_dcm_int(sample_nii,get_dcm_files(sample_dicom_dir)[0],out_path, series_description= "nii2dcm_test1")
    nii_2_dcm_int(sample_nii,get_dcm_files(sample_dicom_dir)[0],out_path, series_description= "nii2dcm_test1")

    C = CommandRunner()
    C.append(["dcm2niix {0}/*".format(out_path)])

    C.run()