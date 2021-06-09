#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import six
import os, sys
import SimpleITK as sitk

import threading
import concurrent.futures

from Std_Tools.pet_processing.radiomics_proc.radiomics_tools3 import extract_radiomics_features
from Std_Tools.common.dataframe_extras import dataframe_int_format


def run_radiomics_by_row(row, bin_widths, image_path_col,mask_path_col, label_val_col = "mask_label"):
        if not isinstance(row,pd.Series):
            raise TypeError

        pet_path = row[image_path_col]
        mask_path = row[mask_path_col]

        label_val = row.get(label_val_col)

        print(row)

        if isinstance(pet_path,str):
            print("Computing radiomics on img '{0}' mask '{1}'...".format(pet_path,mask_path))

        else:
            print("Computing radiomics...")
        if not isinstance(pet_path,sitk.Image):
            img = sitk.ReadImage(pet_path)
        else:
            img = pet_path

        if not isinstance(mask_path, sitk.Image):
            mask = sitk.ReadImage(mask_path)
        else:
            mask = mask_path


        if not isinstance(bin_widths,list):
            bin_widths = [bin_widths]

        # threads = []
        # results = {}
        #
        # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        #     for bw in bin_widths:
        #         # print("using bin width = {0}".format(bw))
        #         threads.append(executor.submit(extract_radiomics_features,img,mask,bw,label_val))
        #
        #     results_list = [t.result() for t in threads]
        #
        #     for bw,result in zip(bin_widths, results_list):
        #         try:
        #             results[bw] = pd.Series(result)
        #         except concurrent.futures.CancelledError as C:
        #             print(str(C))
        #             results[bw] = pd.Series()
        #             continue

        results = {}
        for bw in bin_widths:
            try:
                res = extract_radiomics_features(img,mask,bw,label_val)
                if res:
                    results[bw] = pd.Series(res)
            except Exception as E:
                print(str(E))
                results[bw] = pd.Series()
                continue

        return results

def run_radiomics_on_csv(csv_path, image_path_col = "pet_path", mask_path_col = "mask_path",  bin_width_list = None):
    if not os.path.exists(csv_path):
        raise IOError

    orig_df = pd.read_csv(csv_path,encoding="utf-8")

    if not isinstance(orig_df,pd.DataFrame):
        raise TypeError

    orig_cols = orig_df.columns.to_list()

    if not isinstance(bin_width_list,list):
        bin_width_list = [0.2, 0.1, 0.05, 0.025]

    result_df_dict = dict([(bw,pd.DataFrame()) for bw in bin_width_list])

    # orig_df = orig_df.head(5)
    # orig_df = orig_df[(orig_df["sid"]=="p008") & (orig_df["n"]==1 )]

    for index,row in orig_df.iterrows():
        results = run_radiomics_by_row(row,bin_width_list,image_path_col=image_path_col,mask_path_col=mask_path_col)
        for bw in bin_width_list:
            if bw in results.keys():
                new_row = row.append(results[bw])
                new_cols = results[bw].index.to_list()
                result_df_dict[bw] = result_df_dict[bw].append(new_row,ignore_index=True)[orig_cols+new_cols]
            else:
                result_df_dict[bw] = result_df_dict[bw].append(row,ignore_index=True)

    for bw in bin_width_list:
        out_path = os.path.join(os.path.dirname(csv_path),"radiomics_bw_{:.3f}".format(bw).replace(".","_")+".csv")
        df = result_df_dict[bw]
        dataframe_int_format(df).to_csv(out_path,encoding="utf-8",index = False,float_format='%.5f')

def run_regional_radiomics_on_csv(csv_path, image_path_col = "pet_path", mask_path_col = "mask_path",
                                  label_val_col = "label", bin_width_list = None):
    if not os.path.exists(csv_path):
        raise IOError

    orig_df = pd.read_csv(csv_path,encoding="utf-8")

    if not isinstance(orig_df,pd.DataFrame):
        raise TypeError

    orig_cols = orig_df.columns.to_list()

    if not isinstance(bin_width_list,list):
        bin_width_list = [0.2, 0.1, 0.05, 0.025]

    #cache masks
    print("loading masks...")
    masks = orig_df[mask_path_col].unique()
    masks_dict = dict([(mask, sitk.ReadImage(mask)) for mask in masks])

    result_df_dict = dict([(bw,pd.DataFrame()) for bw in bin_width_list])

    # orig_df = orig_df.head(1)
    # orig_df = orig_df[(orig_df["sid"]=="p008") & (orig_df["n"]==1 )]

    sids = orig_df["sid"].unique()
    for sid in sids:
        sid_rows = orig_df[orig_df["sid"] == sid]
        ns = sid_rows["n"].unique()

        for n in ns:
            sid_n_rows = sid_rows[sid_rows["n"]==n]

            #cache images
            print("loading images for subject '{0}' measurement '{1}'...".format(sid,n))
            images = sid_n_rows[image_path_col].unique()
            images_dict = dict([(image, sitk.ReadImage(image)) for image in images])

            for index,row in sid_n_rows.iterrows():
                mask_path = row[mask_path_col]
                row[mask_path_col] = masks_dict[mask_path]

                image_path = row[image_path_col]
                row[image_path_col] = images_dict[image_path]

                results = run_radiomics_by_row(row,bin_width_list,image_path_col=image_path_col,mask_path_col=mask_path_col, label_val_col= label_val_col)

                # print(results)

                row[mask_path_col] = mask_path
                row[image_path_col] = image_path

                for bw in bin_width_list:
                    if bw in results.keys():
                        new_row = row.append(results[bw])
                        new_cols = results[bw].index.to_list()
                        result_df_dict[bw] = result_df_dict[bw].append(new_row,ignore_index=True)[orig_cols+new_cols]
                    else:
                        result_df_dict[bw] = result_df_dict[bw].append(row,ignore_index=True)

        for bw in bin_width_list:
            out_path = os.path.join(os.path.dirname(csv_path),"radiomics_bw_{:.3f}".format(bw).replace(".","_")+".csv")
            df = result_df_dict[bw]
            if os.path.isfile(out_path):
                dataframe_int_format(df).to_csv(out_path,encoding="utf-8",index = False,float_format='%.5f', mode="a", header=False)
            else:
                dataframe_int_format(df).to_csv(out_path,encoding="utf-8",index = False,float_format='%.5f')



def main():
    # run_radiomics_on_csv("/data/dopa-onco/stat/pet_compare/mask_data.csv")
    # run_regional_radiomics_on_csv("/data/epi-test/stats/radiomics/epiteam/epi-radiomics-masks.csv", bin_width_list=[10,5,2.5,1])
    run_regional_radiomics_on_csv("/data/epi-test/stats/radiomics/aicha/radiomics-masks.csv", bin_width_list=[10,5,2.5,1])

    pass

if __name__ == '__main__':
    main()
