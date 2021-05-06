#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from optparse import OptionParser
import csv
import numpy as np
sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner
from Std_Tools.common.colorPrint import *
from Std_Tools.common.py_io import py_remove
from Std_Tools import extendable_file as ex

def nii2niigz_mri_convert_cmd(in_file, rm=False):
    """
    :param in_file: input file
    :param out_file: output file

    :return: command line command
    """
    if not os.path.exists(str(in_file)):
        printWarning("Conversion failed! '{0}' not exists!".format(str(in_file)))
        return
    if not(ex(in_file).format.endswith(".gz")):
        out_file = ex(in_file)
        out_file.format = out_file.format+".gz"

        cmd = "mri_convert {i} {o} ".format(i=str(in_file), o=str(out_file))
        C = CommandRunner()
        C+=[cmd, out_file]
        C.run()

        if rm:
            py_remove(in_file)

    else:
        printInfo("File {0} already compressed to '.nii.gz' ".format(in_file))

def nii2niigz_fsl_cmd(in_file, rm=False, try_to_find_no_gz = True):
    """
    :param in_file: input file
    :param out_file: output file

    :return: command line command
    """
    if not os.path.exists(str(in_file)):
        if try_to_find_no_gz:
            if ex(in_file).format.endswith(".gz"):
                in_file = ex(str(in_file[:-3]))
            if not os.path.exists(str(in_file)):
                printWarning("Conversion failed! '{0}' not exists!".format(str(in_file)))
                return
        else:
            printWarning("Conversion failed! '{0}' not exists!".format(str(in_file)))
            return


    if not(ex(in_file).format.endswith(".gz")):
        out_file = ex(in_file)
        out_file.format = out_file.format+".gz"

        if rm:
            cmd = "fslchfiletype NIFTI_GZ {i}".format(i=str(in_file), o=str(out_file))
            C = CommandRunner()
            C += [cmd, out_file]
            C.run()
        else:
            cmd = "fslchfiletype NIFTI_GZ {i} {o} ".format(i=str(in_file), o=str(out_file))
            C = CommandRunner()
            C += [cmd, out_file]
            C.run()

    else:
        printInfo("File {0} already compressed to '.nii.gz' ".format(in_file))