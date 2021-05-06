#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
import pandas as pd
import numpy as np
from  scipy import stats
import copy

from Std_Tools.common.colorPrint import *
from Std_Tools import extendable_file as ex
from Std_Tools.common.py_io import py_mkdirs

#dataframe dictionary
def append_df_dicts(df_dict_collector,df_dict_new):
    if not isinstance(df_dict_collector, dict):
        raise TypeError

    if not isinstance(df_dict_new,dict):
        raise TypeError

    df_dict_collector = copy.copy(df_dict_collector)

    for new_key,new_df in df_dict_new.iteritems():
        if new_key not in df_dict_collector.keys():
            df_dict_collector[new_key] = pd.DataFrame()

        if not isinstance(new_df,pd.DataFrame):
            printWarning("Warning! Dictionary element '{0}' is not a pandas.DataFrame!".format(new_key))
            continue

        df_dict_collector[new_key] = df_dict_collector[new_key].append(new_df,ignore_index = True)

    return df_dict_collector


def save_df_dicts(df_dict,save_path,pre_extension = "", make_dirs = True, append = True):
    if not os.path.isdir(str(save_path)):
        if make_dirs:
            py_mkdirs(save_path)
        else:
            raise IOError

    if not isinstance(df_dict,dict):
        raise TypeError

    for key,value in df_dict.iteritems():
        if not isinstance(value, pd.DataFrame):
            printWarning("Warning! Dictionary element '{0}' is not a pandas.DataFrame!".format(key))
            continue

        if len(value.index.tolist())==0:
            printWarning("Warning! Dictionary element '{0}' is empty!".format(key))
            continue

        if pre_extension =="":
            path = os.path.join(save_path,"{0}.csv".format(key))
        else:
            path = os.path.join(save_path, "{1}-{0}.csv".format(key,str(pre_extension)))

        if ex(path).exists() and append:
            value.to_csv(path,index=False,header=False,mode="a")

        else:
            value.to_csv(path, index=False)


def get_df_constant_col_values(df):
    if not isinstance(df, pd.DataFrame):
        raise TypeError

    columns_with_constant_value = df.columns[df.nunique() <= 1]
    constant_values = df.loc[df.index.values[0],columns_with_constant_value]
    return constant_values

def append_series_with_extra(series_to_append,series_with_extra_values):
    if not isinstance(series_to_append,pd.Series):
        raise TypeError
    if not isinstance(series_with_extra_values,pd.Series):
        raise TypeError

    extra_values = series_with_extra_values[[k for k in series_with_extra_values.keys() if k not in series_to_append.keys()]]
    merged_with_extra = series_to_append.append(extra_values)

    return merged_with_extra

def df_fill_with_constant_col(df,constants,drop_na=True):
    if not isinstance(df,pd.DataFrame):
        raise TypeError
    na_cols = df.columns[df.isna().all()].tolist()
    na_cols = [c for c in na_cols if c in constants.keys()]
    if drop_na:
        _df = df.drop(columns=na_cols)
    else:
        _df = df.copy()
    merged_df = pd.DataFrame()
    for index, row in _df.iterrows():
        merged_df = merged_df.append(append_series_with_extra(row,constants),ignore_index=True)

    return merged_df

#stat test

def wide_dataframe_t_test(wide_df,reference_df= None, id_col_name="sid",reference_id_start = "c",**kwargs):
    if not isinstance(wide_df,pd.DataFrame):
        try:
            wide_df = pd.read_csv(str(wide_df))
            if not isinstance(wide_df,pd.DataFrame):
                raise TypeError
        except:
            return

    if isinstance(reference_df,type(None)):
        _df = copy.copy(wide_df)
        _df["is_ref"] = _df[id_col_name].apply(lambda x: str(x).startswith(reference_id_start))

        reference_df = _df.loc[_df["is_ref"],_df.columns.tolist()[:-1]]
        reference_df= reference_df.reset_index(drop=True)

        wide_df = _df.loc[_df["is_ref"]==False,_df.columns.tolist()[:-1]]
        wide_df = wide_df.reset_index(drop=True)

    elif not isinstance(reference_df, pd.DataFrame):
        return

    T_stat_df = copy.copy(wide_df)
    for index,row in wide_df.iterrows():
        for c in wide_df.columns.tolist():
            if c== id_col_name:
                continue
            ref_values = reference_df[c].tolist()
            mean_value = row[c]
            T_stat= stats.ttest_1samp(ref_values,mean_value)

            T_stat_df.loc[index, c] = T_stat.statistic
    return T_stat_df

def df_dict_t_test(wide_df_dict,**kwargs):
    if not isinstance(wide_df_dict,dict):
        return

    T_df_dict = {}

    for df_name, df in wide_df_dict.iteritems():
        t_name = "T-{0}".format(df_name)
        T_df_dict[t_name] = wide_dataframe_t_test(df,**kwargs)
    return T_df_dict


##representation...

def dataframe_int_format(df):
    if not isinstance(df,pd.DataFrame):
        return df

    cols = df.columns.to_list()
    for c in cols:
        try:
            formatted = np.array(df[c].apply(lambda x: int(x)).to_list())
            orig = np.array(df[c].to_list())
            if np.all(np.equal(formatted,orig)):
                df[c] = df[c].apply(lambda x: int(x))
        except:
            continue
    return df[cols]


if __name__ == '__main__':
    wide_dataframe_t_test("/data/epi-test/stats/reg_stats/nis2awR2-pet-1-wide.csv")
