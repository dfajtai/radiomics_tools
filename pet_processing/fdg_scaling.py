#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import numpy as np

sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common.command_runner.command_runner import CommandRunner
from Std_Tools.common.colorPrint import *
from Std_Tools.img_proc.IO.img_reader import read_image
from Std_Tools.pet_processing.pet_scaling_indices import get_global_scaling_indices,get_proportional_scaling_indices


def fdg_convert_to_kilo(in_nii,out_nii=""):
    printInfo("Scaling pet image '{0}' to kBq ...".format(str(in_nii)))

    if not CommandRunner.runSwitch:
        return

    I = read_image(in_nii)
    if not I:
        return
    mean = np.mean(I.data[I.data>10])
    if mean<1000:
        printExtra("Filtered image mean < 1000, so the image is already in kBq scale.")
        return
    else:
        I.factor_scaling(0.001)

    if out_nii != "":
        I.save(out_nii)

    return I.data

def fdg_is_kBq(pet_image_path):
    if not CommandRunner.runSwitch:
        return False

    I = read_image(pet_image_path)
    mean = np.mean(I.data[I.data > 10])
    if mean < 1000:
        return True
    return False






