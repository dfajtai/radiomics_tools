#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner
from Std_Tools.common.colorPrint import *
from Std_Tools import extendable_file as ex



def mnc2nii(in_mnc, out_nii, run = True):
    """
    :param source: input mnc
    :param out: output nii
    :return:
    """

    if os.path.exists(in_mnc):
        if os.path.splitext(in_mnc) == ".nii":
            return

        if CommandRunner.overwrite and os.path.exists(out_nii) and CommandRunner.runSwitch:
            os.remove(out_nii)
        command = "mnc2nii -nii " + in_mnc + " " + out_nii
        C = CommandRunner()
        C += [command, out_nii]
        if run:
            C.run()
        return C
    else:
        printWarning("Warning! File '{0}' not exists!".format(str(in_mnc)))

def mnc2nii_w_mri_convert(in_mnc, out_nii, run = True):
    """
    :param source: input mnc
    :param out: output nii
    :return:
    """

    if os.path.exists(in_mnc):
        if os.path.splitext(in_mnc) == ".nii":
            return

        if CommandRunner.overwrite and os.path.exists(out_nii) and CommandRunner.runSwitch:
            os.remove(out_nii)
        command = "mri_convert " + in_mnc + " " + out_nii
        C = CommandRunner()
        C += [command, out_nii]
        if run:
            C.run()
        return C
    else:
        printWarning("Warning! File '{0}' not exists!".format(str(in_mnc)))

def mnc2nii_convert_bellow(in_mnc, run = True):
    if os.path.exists(in_mnc):
        if os.path.splitext(in_mnc) == ".nii":
            return
        out_nii = ex(in_mnc).lower_base()
        out_nii.format=".nii"

        if CommandRunner.overwrite and os.path.exists(out_nii.s) and CommandRunner.runSwitch:
            os.remove(out_nii.s)

        command = "mnc2nii -nii " + in_mnc + " " + out_nii.s
        C = CommandRunner()
        C+= [command,out_nii.s]
        if run:
            C.run(autoClear=False)
        return C
    else:
        printWarning("Warning! File '{0}' not exists!".format(str(in_mnc)))


def mnc2nii_convert_bellow_w_mri_convert(in_mnc, run = True):
    if os.path.exists(in_mnc):
        if os.path.splitext(in_mnc) == ".nii":
            return
        out_nii = ex(in_mnc).lower_base()
        out_nii.format=".nii"

        if CommandRunner.overwrite and os.path.exists(out_nii.s) and CommandRunner.runSwitch:
            os.remove(out_nii.s)

        command = "mri_convert " + in_mnc + " " + out_nii.s
        C = CommandRunner()
        C+= [command,out_nii.s]
        if run:
            C.run(autoClear=False)
        return C
    else:
        printWarning("Warning! File '{0}' not exists!".format(str(in_mnc)))

def mnc2nii_convert_with_dir(in_mnc, out_nii):
    if os.path.exists(in_mnc):
        if os.path.splitext(in_mnc) == ".nii":
            return

        if CommandRunner.overwrite and os.path.exists(out_nii) and CommandRunner.runSwitch:
            os.remove(out_nii)
        outName = os.path.basename(out_nii)
        mncDir = os.path.join(os.path.dirname(out_nii),"mnc")
        if not os.path.exists(mncDir): os.makedirs(mncDir)
        mncPath= os.path.join(mncDir,outName.replace(".nii",".mnc"))

        if not os.path.exists(mncPath):
            print("Create new link for {0}".format(mncPath))
            os.symlink(in_mnc,mncPath)

        command = "mnc2nii -nii " + mncPath + " " + out_nii
        C = CommandRunner()
        C+= [command,out_nii]
        C.run()
    else:
        printWarning("Warning! File '{0}' not exists!".format(str(in_mnc)))


def nii2mnc(in_nii="", out_mnc=""):
    """
    :param source: source nii file, can be in different directory...

    :param overWrite:
    :return: runnable bash command for conversion
    """
    if os.path.exists(in_nii):
        if os.path.splitext(in_nii) == ".mnc":
            return

        if CommandRunner.overwrite and os.path.exists(out_mnc) and CommandRunner.runSwitch:
            os.remove(out_mnc)
        command = "nii2mnc " + in_nii + " " + out_mnc
        C = CommandRunner()
        C+=[command,out_mnc]
        C.run()
    else:
        printWarning("Warning! File '{0}' not exists!".format(str(in_nii)))


def minc_n_step_corr(in_mnc,out_path=""):
    """
    negative step correction
    :param in_path: input mnc
    :param out_path: output mnc
    :return: runnable bash command list for negative step correction
    """

    if os.path.exists(in_mnc):
        if not os.path.splitext(in_mnc) == ".mnc":
            return

        if out_path == "":
            out_path = in_mnc
        o_path = os.path.dirname(out_path)
        o_name = os.path.basename(out_path)
        temp_name = "tmp-{0}".format(o_name)
        temp_path = os.path.join(o_path,temp_name)
        C = CommandRunner()
        C+="mincreshape -q +dir -dimsize xspace=-1 -dimsize yspace=-1 -dimsize zspace=-1 -dimorder zspace,yspace,xspace -float {i} {o}  -clobber".format(
                i=in_mnc, o=temp_path)
        C+=["mv {0} {1}".format(temp_path,out_path),out_path]
        C.run()

def minc_n_step_corr_4d(in_mnc,out_path=""):
    """
    negative step correction 4d
    :param in_path: input mnc
    :param out_path: output mnc
    :return: runnable bash command list for negative step correction
    """

    if os.path.exists(in_mnc):
        if not os.path.splitext(in_mnc) == ".mnc":
            return

        if out_path == "":
            out_path = in_mnc
        o_path = os.path.dirname(out_path)
        o_name = os.path.basename(out_path)
        temp_name = "tmp-{0}".format(o_name)
        temp_path = os.path.join(o_path, temp_name)
        C = CommandRunner()
        C+="mincreshape -q +dir -dimsize xspace=-1 -dimsize yspace=-1 -dimsize zspace=-1 -dimorder time,zspace,yspace,xspace -float {i} {o}  -clobber".format(
                i=in_mnc, o=temp_path)
        C+=["mv {0} {1}".format(temp_path, out_path),out_path]
        C.run()

def check_negative_step(mnc):
    cmd = "mincinfo -attvalue xspace:step -attvalue yspace:step -attvalue zspace:step {0}".format(mnc)
    op = os.popen(cmd)
    line = op.read()
    spaces = line.split()
    spaces = [float(s) for s in spaces]
    if any([s < 0 for s in spaces]):
        return True
    else:
        return False


