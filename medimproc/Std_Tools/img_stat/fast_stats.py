#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import matplotlib.pyplot as plt
import numpy as np


def array_info(array):
    if isinstance(array,np.ndarray):
        print("Type:\t {0}".format(array.__class__))
        print("Size:\t {0}".format(str(array.size)))
        print("Shape:\t [{0}]".format(",".join([str(s) for s in array.shape])))
        print("Range:\t [{0} {1}]".format(np.min(array),np.max(array)))
        print("Mean:\t {0}".format(str(np.mean(array))))
        print("Std:\t {0}".format(str(np.std(array))))
