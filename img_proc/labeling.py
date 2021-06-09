#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage import morphology
from scipy.ndimage import measurements
import pandas as pd
from copy import copy

sys.path.insert(0, '/home/fajtai/py/')


def labelData(data,struct = None):
    """
    :param data: input matrix
    :type data: np.ndarray
    :return: (labeledData, numOfLabels)

    """
    if isinstance(struct,type(None)):
        struct = morphology.generate_binary_structure(data.ndim,1)

    labeledData, numOfLabels = measurements.label(data,structure=struct)
    return labeledData, numOfLabels

def get_label_with_overlap(labeled_data, mask, only_max_hit = False, hit_percentage_filter = 0):
    """
    This function is stands for filtering labeled data with a binary mask. Only labels overlapped with the given binary mask will be kept.\n
    :param labeled_data: labeled image data
    :param mask: the binary mask, which is filled with 1 in the target region
    :param only_max_hit: if this switch true, the function returns only one label, with the highest mask hit count
    :param hit_percentage_filter: leaves out the labels with hit count less than X percentage (default 50)
    :return: binary mask of the filtered labeled data
    """
    overlap = ((mask*labeled_data)>0).astype("int")
    hits = pd.DataFrame(columns = ["label_value","hit_count"])
    indices=np.argwhere(overlap>0)
    for i in indices:
        label_val = labeled_data[tuple(i)]
        if not any(hits["label_value"]==label_val):
            hits= hits.append({"label_value":label_val, "hit_count":1},ignore_index=True)
        else:
            c = hits.loc[hits["label_value"]==label_val,"hit_count"]
            hits.loc[hits["label_value"] == label_val, "hit_count"] = c+1

    if only_max_hit:
        hits = hits[hits["hit_count"]==np.max(hits["hit_count"])]

    overlap_filtered_labels = np.zeros_like(labeled_data)

    # print(hits)
    for _,row in hits.iterrows():
        label_indices = labeled_data==row["label_value"]
        if hit_percentage_filter>0:
            if np.sum(label_indices)*hit_percentage_filter/100<= row["hit_count"]:
                overlap_filtered_labels[label_indices]=1
        else:
            overlap_filtered_labels[label_indices]=1

    return overlap_filtered_labels

def get_label_stats(sample,binary_masks,is_labeled=False,ignore_zero = True):
    if not isinstance(binary_masks, np.ndarray) or not isinstance(sample,np.ndarray):
        raise TypeError

    if binary_masks.shape != sample.shape:
        raise IndexError("Sample and mas must have the same size!")

    if not is_labeled:
        labeled_data, num_of_labels = labelData(binary_masks)
        if ignore_zero:
            labels = np.arange(1, num_of_labels+1, dtype="int")
        else:
            labels = np.arange(0, num_of_labels+1, dtype="int")
    else:
        labeled_data = binary_masks
        labels = np.unique(labeled_data)
        if ignore_zero:
            labels = labels[labels!=0]

    df_list = []

    for L in labels:
        ind = labeled_data==L

        df_list.append({"label":L,
                        "count":np.sum(ind),
                        "mean":np.mean(sample[ind]),
                        "min":np.min(sample[ind]),
                        "max":np.max(sample[ind]),
                        "sd":np.std(sample[ind])})
    df = pd.DataFrame(df_list)

    return labeled_data, df

def labeling_data_with_counts(data,remove_background = True):
    labeledData, _ = ndm.label(data)
    unique,counts = np.unique(labeledData,return_counts=True)
    counts = zip(unique,counts)
    counts = sorted(counts, key=lambda x: x[1], reverse=True)

    if remove_background:
        del(counts[0])

    return labeledData, counts

def labelData_highpass(data,threshold):

    filtered_data = np.zeros_like(data)

    filtered_data[data>threshold]=1

    outData = labelData(filtered_data)
    return outData


def shift_label_indices(orig_label_map, delta):
    if not isinstance(orig_label_map,np.ndarray):
        return orig_label_map

    if delta==0:
        return orig_label_map

    shifted = orig_label_map+delta
    shifted[orig_label_map==0]=0

    return shifted

def merge_label_maps(fix_label_map,shifting_label_map, method = 0, return_start_indices = False):
    """

    :param fix_label_map: fix label map
    :param shifting_label_map: label map, which's indices will be shifted
    :param method: 0 - overlapping label indices will be relabeled\n
    1 - fix label map values overrides shifting label map values\n
    2 - shifting label map values overrides fix label map values
    :param return_start_indices:
    :return: merged label map
    """
    if not isinstance(fix_label_map,np.ndarray):
        return

    if not isinstance(shifting_label_map,np.ndarray):
        return

    if fix_label_map.shape != shifting_label_map.shape:
        return

    F = copy(fix_label_map)
    S = copy(shifting_label_map)

    overlap = np.logical_and(fix_label_map > 0, S > 0).astype("int")

    delta = np.max(fix_label_map)
    overlap_delta = 0

    shifted = shift_label_indices(S,delta)
    merged = None

    if method == 0:
        labeled_overlap,_ = labelData(overlap)
        overlap_delta = np.max(shifted)

        shifted[overlap==1]=0
        F[overlap==1]=0

        shifted_labeled_overlap = shift_label_indices(labeled_overlap,overlap_delta)

        merged = F + shifted + shifted_labeled_overlap

    if method == 1:
        shifted[overlap==1]=0
        merged = F + shifted

    if method == 2:
        F[overlap==1]=0
        merged = F + shifted

    if return_start_indices:
        return merged, [delta+1,overlap_delta+1]

    else:
        return merged

def main():
    # A = np.array([1,0,3,0,2,2])
    # B = np.array([2,0,1,1,1,0])
    #
    # print(merge_label_maps(A,B,method=0))
    # print(merge_label_maps(A,B,method=1))
    # print(merge_label_maps(A,B,method=2))
    pass


if __name__ == '__main__':
    main()
