#!/usr/bin/env python
# -*- coding: utf-8 -*-


import stat
import numpy as np
from Std_Tools.visualization.fast_plots import fast_hist


def percentile_scale(nd_array, percentile_steps = 0.01):
    if not isinstance(nd_array,np.ndarray):
        try:
            nd_array = np.array(nd_array)
        except:
            raise TypeError

    flat = np.sort(nd_array.flatten())


    percentiles = list(np.arange(0,100+percentile_steps,percentile_steps))
    percentile_values = np.percentile(flat,percentiles)

    rescaled = np.interp(flat,percentile_values, percentiles)



    return np.reshape(rescaled,nd_array.shape)

def zscore_scale(nd_array):
    mean = np.mean(nd_array)
    sd = np.std(nd_array)

    return (nd_array-mean)/sd


if __name__ == '__main__':
    sample_data = np.random.randn(np.power(100,3)).reshape(100,100,100)
    sample_data = sample_data+np.abs(np.min(sample_data))
    sample_data[25:75,25:75,25:75] = sample_data[25:75,25:75,25:75]*2


    # P = percentile_scale(sample_data)

    Z = zscore_scale(sample_data)

    fast_hist(sample_data)
    # fast_hist(P)
    fast_hist(Z)
    pass