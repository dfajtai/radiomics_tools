#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import numpy as np
from copy import copy
from sklearn.metrics import confusion_matrix
from scipy.ndimage.measurements import center_of_mass

from types import *

import pandas as pd

from Common.CommandRunner import CommandRunner

from Common.colorPrint import *

from Std_Tools import read_image
from Std_Tools import extendable_file as ex

def dice_coeff(binary_data1,binary_data2):
    if isinstance(binary_data1,NoneType) and isinstance(binary_data2,NoneType):
        return 0

    if not isinstance(binary_data1,np.ndarray):
        return
    if not isinstance(binary_data2, np.ndarray):
        return

    if not binary_data1.shape==binary_data2.shape:
        return

    true_positive = np.sum(binary_data1[binary_data2==1]==1)
    divider = (np.sum(binary_data1)+np.sum(binary_data2))
    if divider == 0:
        return np.NaN
    dice_coeff = 2.0*true_positive/divider

    return dice_coeff


def overlap_count(binary_data1,binary_data2):
    if isinstance(binary_data1,NoneType) and isinstance(binary_data2,NoneType):
        return 0

    if not isinstance(binary_data1,np.ndarray):
        return
    if not isinstance(binary_data2, np.ndarray):
        return

    if not binary_data1.shape==binary_data2.shape:
        return

    true_positive = np.sum(binary_data1[binary_data2==1]==1)

    return true_positive

def overlap_percentage_of_first(binary_data1,binary_data2):
    if isinstance(binary_data1,NoneType) and isinstance(binary_data2,NoneType):
        return 0

    if not isinstance(binary_data1,np.ndarray):
        return
    if not isinstance(binary_data2, np.ndarray):
        return

    if not binary_data1.shape==binary_data2.shape:
        return

    true_positive = np.sum(binary_data1[binary_data2==1]==1)
    s = np.sum(binary_data1)
    if s == 0:
        return 0
    return true_positive / s * 100.0

def overlap_percentage_of_second(binary_data1,binary_data2):
    if isinstance(binary_data1,NoneType) and isinstance(binary_data2,NoneType):
        return 0

    if not isinstance(binary_data1,np.ndarray):
        return
    if not isinstance(binary_data2, np.ndarray):
        return

    if not binary_data1.shape==binary_data2.shape:
        return

    true_positive = np.sum(binary_data1[binary_data2==1]==1)
    s = np.sum(binary_data2)
    if s == 0:
        return 0
    return true_positive / s * 100.0


def perf_measurement(y_actual_data, y_hat_data):
    if not isinstance(y_actual_data, np.ndarray):
        return None,None,None,None
    if not isinstance(y_hat_data, np.ndarray):
        return None,None,None,None

    if not y_actual_data.shape==y_hat_data.shape:
        return None,None,None,None

    TP = 0
    FP = 0
    TN = 0
    FN = 0

    y_actual = y_actual_data.flatten()
    y_hat = y_hat_data.flatten()

    for i in range(len(y_hat)):
        if y_actual[i]==y_hat[i]==1:
           TP += 1
        if y_hat[i]==1 and y_actual[i]!=y_hat[i]:
           FP += 1
        if y_actual[i]==y_hat[i]==0:
           TN += 1
        if y_hat[i]==0 and y_actual[i]!=y_hat[i]:
           FN += 1

    return (TP, FP, TN, FN)

def perf_measurement_2(y_actual_data, y_hat_data):
    if not isinstance(y_actual_data, np.ndarray):
        return None,None,None,None
    if not isinstance(y_hat_data, np.ndarray):
        return None,None,None,None

    if not y_actual_data.shape==y_hat_data.shape:
        return None,None,None,None

    y_actual = y_actual_data.flatten()
    y_hat = y_hat_data.flatten()

    CM = np.array(confusion_matrix(y_actual,y_hat))

    TP = FP = FN = TN = 0

    # multidim
    FP = CM.sum(axis=0) - np.diag(CM)
    FN = CM.sum(axis=1) - np.diag(CM)
    TP = np.diag(CM)
    TN = CM.sum() - (FP + FN + TP)

    # TP = CM[0,0]
    # FP = CM[0,1]
    # FN = CM[1,0]
    # TN = CM[1,1]

    # # Sensitivity, hit rate, recall, or true positive rate
    # TPR = TP / (TP + FN)
    # # Specificity or true negative rate
    # TNR = TN / (TN + FP)
    # # Precision or positive predictive value
    # PPV = TP / (TP + FP)
    # # Negative predictive value
    # NPV = TN / (TN + FN)
    # # Fall out or false positive rate
    # FPR = FP / (FP + TN)
    # # False negative rate
    # FNR = FN / (TP + FN)
    # # False discovery rate
    # FDR = FP / (TP + FP)
    #
    # # Overall accuracy
    # ACC = (TP + TN) / (TP + FP + FN + TN)

    return (TP, FP, TN, FN)

def fast_binary_perf(y_actual_data, y_hat_data):
    if not isinstance(y_actual_data, np.ndarray):
        return None,None,None,None
    if not isinstance(y_hat_data, np.ndarray):
        return None,None,None,None

    if not y_actual_data.shape==y_hat_data.shape:
        return None,None,None,None

    TP = np.sum(np.logical_and([y_actual_data==1],[y_hat_data==1]))
    TN = np.sum(np.logical_and([y_actual_data==0],[y_hat_data==0]))
    FP = np.sum(np.logical_and(y_hat_data,y_actual_data==0))
    FN = np.sum(np.logical_and(y_actual_data,y_hat_data==0))

    return (TP, FP, TN, FN)


def label_map_overlap(M1, M2, overlap_function):
    """
    :param label_map_ndarray_1: first N x M (ndarray) matrix of integer labels
    :param label_map_ndarray_2: second N x M (ndarray) matrix of integer labels
    :param overlap_function: function, or list of functions which measure overlap between two binary mask. signature: (m1,m2)->double/0
    :return: label overlap matrix
    """
    class no_overlap_exception(Exception):
        pass

    if not isinstance(M1, np.ndarray):
        return

    if not isinstance(M2, np.ndarray):
        return

    if M1.shape != M2.shape:
        return

    functions = []
    if not isinstance(overlap_function,list):
        overlap_function = [overlap_function]
    for f in overlap_function:
        if isinstance(f, FunctionType):
            functions.append(f)

    # bounding box search settings: x -> (1,2), y -> (0,2), z -> (0,1)
    bbox_params = [(1,2), (0,2), (0,1)]

    M1_max = np.max(M1)
    M1_values = range(1,int(M1_max)+1,1)
    M1_df_labels = ["M1_{0}".format(v) for v in M1_values]

    M2_max = np.max(M2)
    M2_values = range(1,int(M2_max)+1,1)
    M2_df_labels = ["M2_{0}".format(v) for v in M2_values]

    overlap_matrix = np.zeros((int(M1_max),int(M2_max),len(functions)))

    for v1 in M1_values:
        M1_ = np.zeros_like(M1)
        M1_[M1 == v1] = 1
        M1_bbox = []

        for axis in bbox_params:
            nonzero = np.any(M1_, axis=axis)
            M1_bbox.append(np.where(nonzero)[0][[0,-1]])

        for v2 in M2_values:
            M2_ = np.zeros_like(M2)
            M2_[M2 == v2] = 1

            M2_bbox = []
            try:
                for axis_i in range(len(bbox_params)):
                    axis = bbox_params[axis_i]
                    nonzero = np.any(M2_, axis=axis)
                    axis_limit = np.where(nonzero)[0][[0,-1]]
                    #if  x2' < x1 or x2 < x1'
                    if axis_limit[1] < M1_bbox[axis_i][0] or M1_bbox[axis_i][1] < axis_limit[0]:
                        raise no_overlap_exception
                    M2_bbox.append(axis_limit)

            except no_overlap_exception:
                for k in range(len(functions)):
                    overlap_matrix[v1-1,v2-1,k] = functions[k](None,None)
                continue

            bb = [] # mutual bbox
            for axis_i in range(len(bbox_params)):
                bb.append([min([M1_bbox[axis_i][0],M2_bbox[axis_i][0]]),
                                  max([M1_bbox[axis_i][1], M2_bbox[axis_i][1]])])

            for k in range(len(functions)):
                    overlap_matrix[v1-1,v2-1,k] = functions[k](
                        M1_[bb[0][0]:bb[0][1], bb[1][0]:bb[1][1], bb[2][0]:bb[2][1]],
                        M2_[bb[0][0]:bb[0][1], bb[1][0]:bb[1][1], bb[2][0]:bb[2][1]])

    df_list = [pd.DataFrame(overlap_matrix[:,:,k],index=M1_df_labels, columns=M2_df_labels) for k in range(len(functions))]

    return df_list

def label_map_gravity_distance(M1, M2, distance_function=None):
    """
        :param label_map_ndarray_1: first N x M (ndarray) matrix of integer labels
        :param label_map_ndarray_2: second N x M (ndarray) matrix of integer labels
        :param overlap_function: function, or list of functions which measure distance
        :return: label distance matrix
        """
    if not isinstance(M1, np.ndarray):
        return

    if not isinstance(M2, np.ndarray):
        return

    if M1.shape != M2.shape:
        return

    functions = []

    if distance_function == None:
        distance_function = lambda x,y : np.linalg.norm(np.array(x)-np.array(y))

    if not isinstance(distance_function, list):
        distance_function = [distance_function]
    for f in distance_function:
        if isinstance(f, FunctionType):
            functions.append(f)



    M1_max = np.max(M1)
    M1_values = range(1, int(M1_max) + 1, 1)
    M1_df_labels = ["M1_{0}".format(v) for v in M1_values]
    M1_mask= np.zeros_like(M1)
    M1_mask[M1>0]=1
    M1_centers = center_of_mass(M1_mask,labels=M1,index = M1_values)

    M2_max = np.max(M2)
    M2_values = range(1, int(M2_max) + 1, 1)
    M2_df_labels = ["M2_{0}".format(v) for v in M2_values]
    M2_mask= np.zeros_like(M2)
    M2_mask[M2>0]=1
    M2_centers = center_of_mass(M2_mask,labels=M2, index = M2_values)

    overlap_matrix = np.zeros((int(M1_max), int(M2_max), len(functions)))


    for i in range(len(M1_values)):
        M1_center = M1_centers[i]

        for j in range(len(M2_values)):
            M2_center = M2_centers[j]

            for k in range(len(functions)):
                overlap_matrix[i, j, k] = functions[k](M1_center,M2_center)


    df_list = [pd.DataFrame(overlap_matrix[:, :, k], index=M1_df_labels, columns=M2_df_labels) for k in
               range(len(functions))]

    return df_list