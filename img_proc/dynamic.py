#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner


def time_mean(in_nii,out_nii):
    command = "mri_concat --i " + str(in_nii) + " --o " + str(out_nii) + " --mean"
    C = CommandRunner()
    C+=[command,str(out_nii)]
    C.run()

def motion_corr(in_nii,out_nii):
    command = "mcflirt -in " + str(in_nii) + " -o " + str(out_nii) + " -plots"
    C = CommandRunner()
    C+=[command,str(out_nii)]
    C.run()

def frame_skip(in_nii,out_nii, n = 5):
    command = "mri_convert " + str(in_nii) + " " + str(out_nii) + " --nskip " + str(n)
    C = CommandRunner()
    C+=[command,str(out_nii)]
    C.run()

