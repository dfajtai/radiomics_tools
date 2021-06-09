#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner

from Std_Tools._package_opts_ import *

#***************************************************  FLIRT  ***********************************************************


def invert_xfm(input_mat,output_mat):
    command_path = "/usr/share/fsl/5.0/bin/convert_xfm"
    command = "{c} -omat {output} -inverse {input}".format(c=command_path,output=str(output_mat),input=str(input_mat))
    C = CommandRunner()
    C+=[command,str(output_mat)]
    C.run()


def concat_xfm(in_xfm1, in_xfm2, out_xfm):
    command_path = "/usr/share/fsl/5.0/bin/convert_xfm"
    command = "{c} -concat {in1} -omat {out_xfm} {in2}".format(c=command_path, in1 = str(in_xfm1), in2 = str(in_xfm2),  out_xfm=str(out_xfm))
    C = CommandRunner()
    C+=[command, str(out_xfm)]
    C.run()


def flirt_register(input, ref, out_mat, out_nii, dof, interp="trilinear", cost="corratio", search=[-10,10],**kwargs):
    command = flirtPath

    if out_nii == "":
        command += " -in {input} -ref {ref}  -omat {omat}".format(input=str(input), ref=str(ref), omat=str(out_mat))
    else:
        command+= " -in {input} -ref {ref} -out {out} -omat {omat}".format(input = str(input),ref = str(ref), out = str(out_nii), omat = str(out_mat))

    if dof in [3, 6, 7, 9, 12]:
        command += " -dof " + str(dof)
    search.sort()

    if len(search) == 2:
        if search[0] >= -180 and search[1] <= 180:
            command += " -searchrx " + str(search[0]) + " " + str(search[1]) + " -searchry " + str(
                search[0]) + " " + str(search[1]) + " -searchrz " + str(search[0]) + " " + str(search[1])

    if interp in flirt_interpTypes:
        command += " -interp " + interp

    if cost in flirt_costTypes:
        command += " -cost " + str(cost)

    for k in kwargs:
        if kwargs[k]:
            c = " -{0} {1}".format(str(k), str(kwargs[k]))
        else:
            c = " -{0}".format(str(k))
        command+=c

    C = CommandRunner()
    C+=[command,[str(out_nii), str(out_mat)]]
    C.run()


def flirt_apply_xfm(input,ref,mat_file,out_nii,interp="trilinear"):
    command = flirtPath +" -in {input} -ref {ref} -out {out} -applyxfm -init {init}".format(input = str(input),ref = str(ref), out = str(out_nii), init = str(mat_file))

    if interp in flirt_interpTypes:
        command += " -interp " + interp

    C = CommandRunner()
    C += [command, [str(out_nii)]]
    C.run()