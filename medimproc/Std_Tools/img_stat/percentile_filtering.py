#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
simple python module for Anderson-Darling test based filtering
reference:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.anderson.html#scipy.stats.anderson
https://www.itl.nist.gov/div898/handbook/prc/section2/prc213.htm
"""
import os,sys
from types import NoneType
import math
from copy import copy
from scipy import stats
import numpy as np
from Std_Tools.visualization.fast_plots import fast_hist, fast_lin_plot, fast_point_plot


def percentile_plot(distribution,percentile_level_range):
    if not isinstance(distribution, np.ndarray):
        return

    if not (isinstance(percentile_level_range,list) or isinstance(percentile_level_range,np.ndarray)):
        return

    percentile_level_range = sorted(percentile_level_range)

    percentile_values = [np.percentile(distribution,P_level) for P_level in percentile_level_range]

    fast_point_plot(percentile_level_range,percentile_values)


def anderson_percentile_filter(initial_distribution, percentile_level_range, distribution_form = "gumbel", target_significance = 0.01):
    """
    This function searches for the first percentile value in the percentile range, to achieve a specific level of significance.
    :param initial_distribution: initial values
    :param percentile_level_range: list of percentages
    :param distribution_form: type of suggested distributions. Accepted values = [norm,expon,logistic,gumbel_l,gumbel_r]\n
                              For skewed distribution use logistic, gumbel_l / gumbel_r. gumbel_l =  Generalized Extreme Value distribution Type-I.
    :param target_significance: Target significance level
    :return: ideal percentile value
    """
    if not isinstance(initial_distribution, np.ndarray):
        return

    if not (isinstance(percentile_level_range,list) or isinstance(percentile_level_range,np.ndarray)):
        return

    percentile_level_range = sorted(percentile_level_range)

    for P_level in percentile_level_range:
        percentile = np.percentile(initial_distribution,P_level)
        statistics, critical_values, significance_level = stats.anderson(initial_distribution[initial_distribution>percentile],distribution_form)
        print(statistics, critical_values, significance_level)
        print(percentile)
        # fast_hist(initial_distribution,initial_distribution>percentile)
        print()