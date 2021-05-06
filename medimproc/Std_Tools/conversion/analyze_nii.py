#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from optparse import OptionParser
import csv
import numpy as np
sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common import CommandRunner
from Std_Tools.common.colorPrint import *

def analyze_2_nii(input_path, out_nii=None, gz=False):
    img_name = os.path.splitext(input_path)[0]

    if not (os.path.exists(img_name+".img") and os.path.exists(img_name+".hdr")):
        print("img or hdr missing")
        raise ValueError

    if isinstance(out_nii,type(None)):
        out_nii=img_name+".nii"

    if gz and not str(out_nii).endswith(".gz"):
        out_nii+=".gz"

    C = CommandRunner()
    C+=["mri_convert -i {i} -o {o}".format(i = img_name+".hdr", o=out_nii),out_nii]
    C.run()