#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from optparse import OptionParser
import csv
import numpy as np
sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner
from Std_Tools.common.colorPrint import *

def mgz2nii_cmd(in_file, out_file, orientation = "RAS", like = "", transform = "",  **options):
    """
    :param in_file: input file
    :param out_file: output file
    :param orientation: RAS
    :param like: matches size, voxel dimensions
    :param transform: transformation file
    :param options: additional options
    :return: command line command
    """
    if not os.path.exists(in_file):
        printWarning("Conversion failed! '{0}' not exists!".format(str(in_file)))
        return
    options["out_orientation"] = orientation
    options["like"] = like
    options["transform"] = transform
    opts = " ".join(["--{opt} {val}".format(opt=str(k),val = str(options[k])) for k in options.keys() if str(options[k]) != ""])
    cmd = "mri_convert {i} {o} {opts}".format(i=in_file, o=out_file,opts=opts)
    C = CommandRunner()
    C+=[cmd, out_file]
    C.run()


def label_mgz2nii_cmd(in_file, out_file, like = "",  **options):
    """
    :param in_file: input file
    :param out_file: output file
    :param like: matches size, voxel dimensions
    :param options: additional options
    :return: command line command
    """
    if not os.path.exists(str(in_file)):
        printWarning("Conversion failed! '{0}' not exists!".format(str(in_file)))
        return
    options["temp"] = like
    opts = " ".join(["--{opt} {val}".format(opt=str(k),val = str(options[k])) for k in options.keys() if str(options[k]) != ""])
    cmd = "mri_label2vol --seg {i} --o {o} {opts} --regheader {i}".format(i=str(in_file), o=str(out_file),opts=opts)
    C = CommandRunner()
    C+=[cmd,out_file]
    C.run()


def main():
    pass


if __name__ == "__main__":
    main()