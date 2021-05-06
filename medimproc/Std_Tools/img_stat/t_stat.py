#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import numpy as np
from copy import copy
from scipy import stats


from Common.CommandRunner import CommandRunner
from Common.colorPrint import *
from Std_Tools import read_image
from Std_Tools import extendable_file as ex
from Std_Tools.img_proc.neighbours import neighbours_3x3


def df(n1,n2):
    return n1+n2-2

def t_critical(p,df):
    return stats.t.ppf(p, df)

def __vox_t_test(sample, ref):
    T = stats.ttest_1samp(ref.T, sample).statistic
    return T

def t_stat_data(reference_data,measured_data,domain):
    if not isinstance(reference_data, np.ndarray):
        return
    if not isinstance(measured_data,np.ndarray):
        return
    if not isinstance(domain,np.ndarray):
        return

    if not domain.shape == reference_data.shape == measured_data.shape:
        return

    # vectorized_vox_t_test = np.vectorize(vox_t_test)

    if np.sum(domain) == 0:
        return np.zeros_like(domain)

    t_stat_data = np.zeros_like(domain).astype("float64")
    indices = np.argwhere(domain>0)

    for i in indices:
        t_stat_data[tuple(i)]=__vox_t_test(measured_data[tuple(i)],reference_data[domain.astype("bool")])

    # t_stat_data = vectorized_vox_t_test(measured_data,reference_data)

    return t_stat_data


def t_stat_data_N27(reference_data,measured_data,domain):
    if not isinstance(reference_data, np.ndarray):
        return
    if not isinstance(measured_data,np.ndarray):
        return
    if not isinstance(domain,np.ndarray):
        return

    if not domain.shape == reference_data.shape == measured_data.shape:
        return

    if np.sum(domain) == 0:
        return np.zeros_like(domain)

    t_stat_data = np.zeros_like(domain).astype("float64")
    indices = np.argwhere(domain>0)

    for i in indices:
        ref = np.array([reference_data[n] for n in neighbours_3x3(i,domain.shape,add_center=True)])
        t_stat_data[tuple(i)]=__vox_t_test(measured_data[tuple(i)],ref)

    return t_stat_data



def t_from_dist(sample_ndarray,ref_dist,sample_mask=None):
    if not isinstance(sample_ndarray,np.ndarray):
        return
    if not isinstance(ref_dist, np.ndarray):
        return
    ref_dist = ref_dist.flatten()


    if isinstance(sample_mask,np.ndarray):
        indices = np.argwhere(sample_mask > 0)
        t_map = np.zeros_like(sample_ndarray)
        for i in indices:
            t_map[tuple(i)]= __vox_t_test(sample_ndarray[tuple(i)],ref_dist)
        return t_map
    else:
        vectorized_vox_t_test = np.vectorize(__vox_t_test,excluded=["ref","sample_mask"])
        return vectorized_vox_t_test(sample_ndarray,ref=ref_dist)

def t_stat_dict_of_lists(ref_dict_list,sample_dict_list, index_col = "index"):
    if not isinstance(ref_dict_list,dict):
        return
    if not isinstance(sample_dict_list,dict):
        return
    mutual_keys = set.intersection(set(ref_dict_list.keys()),set(sample_dict_list.keys()))

    t_stat_df = pd.DataFrame(columns = [index_col,"t","p"])

    for k in mutual_keys:
        try:
            index = np.int(k)
            ref = np.array(ref_dict_list[k])
            sample = np.array(sample_dict_list[k])
            stat_test_result = stats.ttest_ind(ref,sample)
            p = stat_test_result.pvalue
            t = stat_test_result.statistic
            t_stat_df = t_stat_df.append(pd.Series({index_col:index,"p":p,"t":t}),ignore_index=True)
        except:
            continue
    return t_stat_df

def main():
    pass


if __name__ == '__main__':
    main()