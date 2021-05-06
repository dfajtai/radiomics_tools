#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import re
import numpy as np
import scipy.stats as stats
import copy
import h5py

from Std_Tools.common.list_functions import unwrapList

def append_dict_nested_lists(dict_1,dict_2):
    if not isinstance(dict_1,dict):
        return

    if not isinstance(dict_2,dict):
        return

    appended= {}
    for k1 in dict_1.keys():
        v = unwrapList(dict_1[k1])
        if not isinstance(v,list):
            appended[k1]=[v]
        else:
            appended[k1]= v


    for k2 in dict_2.keys():
        v = unwrapList(dict_2[k2])
        if k2 not in appended.keys():
            if not isinstance(v, list):
                appended[k2] = [v]
            else:
                appended[k2] = v

        else:
            if not isinstance(v, list):
                appended[k2].append(v)
            else:
                appended[k2].extend(v)


    return appended

if __name__ == '__main__':
    A = {"asd":[[1],2,3,4],"qwe":[12341234]}
    B = {"qwe":[[[12356]],[123]],"egdfg":1}

    print(append_dict_nested_lists(B,B))