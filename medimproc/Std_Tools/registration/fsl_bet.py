#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os

sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner
from Std_Tools._package_opts_ import *
from Std_Tools import extendable_file as ex
from Std_Tools.common.py_io import py_mkdirs, py_copy
from Std_Tools.img_proc import read_image

#***************************************************   BET   ***********************************************************


def bet_clean_fmri(input, out_nii, threshold = 0.5, threshold_gradient = 0):
    command = bet_path + \
              " {inNii} {outNii} -F -f {threshold} -g {gradient}".format(inNii=str(input), outNii=str(out_nii),
                                                                         threshold=str(threshold),
                                                                         gradient=str(threshold_gradient))

    C = CommandRunner()
    C+=[command,[str(out_nii)]]
    C.run()


def bet_brain_extract(input, brain , brain_mask, threshold = 0.5, threshold_gradient = 0):
    command = bet_path + " {inNii} {outNii} -R -B -t -f {threshold} -g {gradient}".format(inNii=str(input), outNii=str(brain),
                                                                         threshold=str(threshold),
                                                                         gradient=str(threshold_gradient))

    if brain_mask:
        command += " -m"

    C = CommandRunner()
    C+=[command,[str(brain),str(brain_mask)]]
    C.run()
