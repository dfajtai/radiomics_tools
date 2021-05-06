#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os

sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner
from Std_Tools._package_opts_ import *
from Std_Tools import extendable_file as ex
from Std_Tools.common.py_io import py_mkdirs, py_copy
from Std_Tools.img_proc import read_image

class FastResult:
    def __init__(self,restored,GM="",WM="",CSF = ""):
        """
        :param restored: bias field corrected brain
        :param GM: gray matter
        :param WM: white matter
        :param CSF: cerbero spinal fluid
        """
        self.restored = restored
        self.GM = GM
        self.WM = WM
        self.CSF = CSF
#***************************************************  FAST  ************************************************************

def fsl_fast_bias_corr(brain_path,bias_corrected_path="", n=3):
    """
    Files generated: dir[bias_corrected_path]/FAST/brain...
        ..._mixeltype.nii
        ..._pve_0.nii - csf
        ..._pve_1.nii - gm
        ..._pve_2.nii - wm
        ..._pveseg.nii
        ..._restore.nii -> bias field corrected image
        ..._seg.nii\n

    :param brain_path: path of brain extracted form T1
    :param bias_corrected_path: path of bias field corrected brain
    :param n: number of distributions (default 3)
    :return: CommandRunner
    """

    if bias_corrected_path =="":
        bias_corrected_path= ex(brain_path)*"BCorr"

    out_dir = os.path.join(ex(bias_corrected_path).base_path,"FAST")
    py_mkdirs(out_dir)

    out_path = os.path.join(out_dir,"brain")

    command = "{fast} -t 1 -n {n} -H 0.1 -I 4 -l 20.0 -B -o {out_path} {in_file}".format(fast=fsl_fast_path, n=str(n),out_path = str(out_path),in_file=str(brain_path))
    C = CommandRunner()
    C.Commands.append([command])
    C.run()

    py_copy(out_path+"_restore.nii",bias_corrected_path)

    return FastResult(restored=bias_corrected_path)


def fsl_fast_bias_corr_with_seg(brain_path, bias_corr_path="", gm ="", wm="", csf="", n=3):
    """
    Files generated: dir[bias_corr_path]/FAST/brain...
        ..._mixeltype.nii
        ..._pve_0.nii - csf
        ..._pve_1.nii - gm
        ..._pve_2.nii - wm
        ..._pveseg.nii
        ..._restore.nii -> bias field corrected image
        ..._seg.nii\n

    :param brain_path: path of brain extracted form T1
    :param bias_corr_path: path of bias field corrected brain
    :param gm: gray matter path
    :param wm: white matter path
    :param csf: cerbero spinal fluid path
    :param n: number of distributions (default 3)

    :return: FastResults
    """


    if bias_corr_path == "":
        bias_corr_path= ex(brain_path) * "BCorr"

    out_dir = os.path.join(ex(bias_corr_path).base_path, "FAST")
    py_mkdirs(out_dir)

    out_path = os.path.join(out_dir,"brain")

    command = "{fast} -t 1 -n {n} -H 0.1 -I 4 -l 20.0 -B -o {out_path} {in_file}".format(fast=fsl_fast_path, n=str(n),out_path = str(out_path),in_file=str(brain_path))
    C = CommandRunner()
    C.Commands.append([command])
    C.run()

    # CommandRunner.set_run_switch(sim=False)

    py_copy(out_path +"_restore.nii", bias_corr_path)

    F = FastResult(restored=bias_corr_path)

    #CSF
    p = out_path + "_pve_0.nii"
    if ex(p).exists():
        I = read_image(p)
        I.threshold(0.5)
        if csf == "":
            csf = ex(brain_path)
            csf.mod = "fCSF"
        I.save(csf)
        F.CSF=csf

    #GM
    p = out_path + "_pve_1.nii"
    if ex(p).exists():
        I = read_image(p)
        I.threshold(0.5)
        if gm == "":
            gm = ex(brain_path)
            gm.mod = "fGM"
        I.save(gm)
        F.GM=gm

    #WM
    p = out_path + "_pve_2.nii"
    if ex(p).exists():
        I = read_image(p)
        I.threshold(0.5)
        if wm == "":
            wm = ex(brain_path)
            wm.mod = "fWM"
        I.save(wm)
        F.WM=wm

    return F