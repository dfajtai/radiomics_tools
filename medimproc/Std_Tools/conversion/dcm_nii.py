#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from optparse import OptionParser
import csv
import numpy as np
sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner
from Std_Tools.common.colorPrint import *
from Std_Tools.common.py_io import py_copy,py_remove, py_mkdirs, py_link, py_rm_tree
from Std_Tools.StudyHelper.path_handler import extendable_file as ex

def dcm_dir_2_niix(dcm_path,out_nii):
    """
    Converts a directory with a single series of dcm files into a nifti image
    :param dcm_path: dcm directory
    :param out_nii: output nifti path
    :return: True
    """
    if not os.path.isdir(dcm_path):
        return False

    cmd = "dcm2niix -f tmp/{out}_%s {path}/*".format(path = dcm_path, out= ex(out_nii).file_name)
    C = CommandRunner()
    C+=[cmd,""]
    C.run()

    tmp_files = os.listdir(os.path.join(dcm_path, "tmp"))
    nii_files = list(filter(lambda x : str(x).endswith(".nii"),tmp_files))

    if len(nii_files)<1:
        return False

    py_copy(os.path.join(dcm_path, "tmp", nii_files[0]), out_nii,overwrite=CommandRunner.overwrite)
    py_remove(tmp_files)

    return True


def dcm2niix_by_files(dcm_files, out_nii):
    target_files = [df for df in dcm_files if os.path.isfile(df)]
    if len(target_files)==0:
        return False

    tmp_dir = os.path.join(ex(out_nii).base_path,"tmp")
    py_mkdirs(tmp_dir)

    for t in target_files:
        py_link(t, ex(t).change_base(tmp_dir))

    cmd = 'dcm2niix -z y -5 -m y -s y -f {name}_%s {tmp_dir}'.format(name = str(ex(out_nii).file_name).split(".")[0], tmp_dir = tmp_dir)
    C = CommandRunner()
    C += [cmd, ""]
    C.run()

    tmp_files = os.listdir(tmp_dir)
    nii_files = list(filter(lambda x: str(x).endswith(".nii.gz"), tmp_files))

    if len(nii_files) < 1:
        return False

    py_mkdirs(ex(out_nii).base_path)
    py_copy(os.path.join(tmp_dir, nii_files[0]), out_nii, overwrite=True)
    py_rm_tree(tmp_dir)

    return True