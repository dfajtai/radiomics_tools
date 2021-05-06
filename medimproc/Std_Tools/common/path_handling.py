#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys


sys.path.insert(0, '/home/fajtai/py/')

from Std_Tools.common.colorPrint import *
from Std_Tools.StudyHelper.path_handler import extendable_file as ex

def get_files_with(base_path, file_name_part,all_shortest = True,D = 0):
    if not os.path.isdir(base_path):
        printWarning("Warning! Directory '{0}' not exists.".format(base_path))
        return

    files = os.listdir(base_path)
    base_file_name_part = str(file_name_part).split("*")
    match = [f for f in files if all([m in f for m in base_file_name_part])]
    match_p = [os.path.join(base_path, m) for m in match if m != ""]
    if len(match_p) == 0:
        printWarning("File not found in directory '{0}' with mask '{1}'!".format(str(base_path), file_name_part))
        return

    match_p = sorted(match_p, key=lambda x: len(x))
    min_len = len(match_p[0])

    if all_shortest:
        match_p = [mp for mp in match_p if (len(mp) >= min_len - D and len(mp) <= min_len + D)]

    files = [ex(mp) for mp in match_p]
    return files