#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0,'/home/fajtai/py/')
from Common.CommandRunner import CommandRunner
from Std_Tools._package_opts_ import *

#***************************************************  FNIRT  ***********************************************************


def fnirt_nonlin_reg(input, out_nonlin, ref = "/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain", affine = "",interp = "linear", config = "T1_2_MNI152_2mm", **kwargs):
    command = fnirt_path
    if ref != "":
        command = command + " --ref=" + str(ref)
    command = command + " --in=" + str(input)

    if affine != "":
        command += " --aff=" + str(affine)
    command += " --cout=" + str(out_nonlin)

    if interp in fnirt_interpTypes:
        command += " --interp=" + str(interp)

    if config != "":
        command += " --config=" + str(config)

    for k in kwargs.keys():
        command += " --{0}={1}".format(str(k), str(kwargs[k]))

    C = CommandRunner()
    C+=[command,[str(out_nonlin)]]
    C.run()


def fnirt_applywarp(input, ref, nonlin, out_nii, premat="", interp="trilinear"):
    command = applyWarpPath
    command += " --in="+ str(input) + \
        " --ref=" + str(ref) + \
        " --warp=" + str(nonlin) + \
        " --out=" + str(out_nii)
    if premat!="":
        command+=" --premat=" + str(premat)
    if interp in fnirt_applywarp_InterpTypes:
        command += " --interp=" + interp

    C = CommandRunner()
    C += [command, [str(out_nii)]]
    C.run()