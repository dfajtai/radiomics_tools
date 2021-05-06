#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys

NoneType = type(None)

import math
from copy import copy
from scipy import stats

import matplotlib.pyplot as plt
# import seaborn as sns; sns.set()
import numpy as np

from Common.CommandRunner import CommandRunner
from Common.colorPrint import *
from Std_Tools import read_image
from Std_Tools import extendable_file as ex
from Std_Tools.img_proc.neighbours import neighbours_3x3
from sklearn.mixture import GaussianMixture as GMM
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist

# def sklearn_gmm_test():
#     # Generate some data
#     X, y_true = make_blobs(n_samples=400, centers=4,
#                            cluster_std=0.60, random_state=0)
#     X = X[:, ::-1] # flip axes for better plotting
#
#
#
#     # kmeans = KMeans(4, random_state=0)
#     # labels = kmeans.fit(X).predict(X)
#     # plt.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis')
#
#     kmeans = KMeans(n_clusters=4, random_state=0)
#     plot_kmeans(kmeans, X)
#     plt.show()
#
#
#
#
# def plot_kmeans(kmeans, X, n_clusters=4, rseed=0, ax=None):
#     labels = kmeans.fit_predict(X)
#
#     # plot the input data
#     ax = ax or plt.gca()
#     ax.axis('equal')
#     ax.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis', zorder=2)
#
#     # plot the representation of the KMeans model
#     centers = kmeans.cluster_centers_
#     radii = [cdist(X[labels == i], [center]).max()
#              for i, center in enumerate(centers)]
#     for c, r in zip(centers, radii):
#         ax.add_patch(plt.Circle(c, r, fc='#CCCCCC', lw=3, alpha=0.5, zorder=1))


def gmm_1d_test():
    X, y_true = make_blobs(n_samples=10000, centers=4, n_features=1,
                           cluster_std=0.9)

    GMM_1d(X)

def GMM_1d(sample_ndarray,n_component_min=1, n_component_max = 10, create_plot = True, show_plot = False, plot_save_path = None, csv_save_path = None):
    """
    This function stands for intensity based clustering of sample data based on Gaussian Mixture Model\n
    :param sample_ndarray: sample data
    :param n_component_min: expected minimal number of components
    :param n_component_max: expected maximal number of components
    :param create_plot: if true, the result will shown on a fancy plot
    :return: ideal gaussian mixture model with minimal number of distribution
    """
    if not isinstance(sample_ndarray,np.ndarray):
        return

    X = sample_ndarray.flatten().reshape(-1, 1)

    n_components = np.arange(n_component_min, n_component_max+1)
    models = [GMM(n, covariance_type='spherical').fit(X)
              for n in n_components]

    M_best = sorted(models, key=lambda x: x.aic(X))[0]
    if not isinstance(M_best, GMM):
        return

    df = pd.DataFrame(columns=["mean","covar","weight"])
    try:
        df = pd.DataFrame({"mean":M_best.means_.flatten(), "covar":M_best.covariances_.flatten(),"weight":M_best.weights_.flatten()})
        df["dist_ind"]= df.index+1
        print(df[["dist_ind","mean","covar","weight"]].sort_values(by=["weight"],ascending=False))
    except:
        printError("Due to an error, distribution parameters can not be printed")

    if not isinstance(csv_save_path,NoneType):
        df.to_csv(str(csv_save_path), index=False)
        printInfo("Saving GMM info to csv '{0}'".format(csv_save_path))


    if not create_plot:
        return M_best

    pred = M_best.predict(X)
    count = max(math.ceil(math.log10(np.max(X) - np.min(X))) * 10,30)
    bins = np.linspace(np.min(X), np.max(X), count)

    plt.close("all")
    fig = plt.figure()

    # plot 1
    plt1 = plt.subplot(221)
    plt1.hist(X, bins=bins)
    plt1.grid(True)
    plt1.set_title("Starting distribution")

    # plot 2
    plt2 = plt.subplot(222)
    plt2.plot(n_components, [m.bic(X) for m in models], label='BIC')
    plt2.plot(n_components, [m.aic(X) for m in models], label='AIC')
    plt2.grid(True)
    plt2.legend(loc='best')
    plt2.set_xlabel("Number of components")
    plt2.set_title("Searching for ideal number of components")

    # plot 3
    plt3 = plt.subplot(212)
    x = [X[pred == i] for i in range(M_best.n_components)]
    label = ["G_{0}".format(str(i + 1)) for i in range(M_best.n_components)]
    if len(x)==1:
        x=x[0]
    plt3.hist(x, alpha=1, bins=bins, label=label)
    plt3.grid(True)
    plt3.legend(loc="upper right")
    plt3.set_title("Gaussian distributions, N = {0}".format(str(M_best.n_components)))

    plt.tight_layout()
    if show_plot:
        fig.show()

    if not isinstance(plot_save_path,NoneType):
        printInfo("Saving GMM plot to csv '{0}'".format(plot_save_path))
        plt.savefig(str(plot_save_path),dpi=300)

    plt.close()

    return M_best

def gmm_predict_img(gmm, image_data,mask = None, keep_best =True):
    if not isinstance(gmm, GMM):
        return

    df = pd.DataFrame(columns=["mean", "covar", "weight"])
    try:
        df = pd.DataFrame({"mean": gmm.means_.flatten(), "covar": gmm.covariances_.flatten(),
                           "weight": gmm.weights_.flatten()})
    except:
        printError("Due to an error, distribution parameters can not be printed")

    predict = lambda x: gmm.predict(x)+1
    gmm_predict_map = np.vectorize(predict)

    if isinstance(mask,np.ndarray):
        indices = np.argwhere(mask > 0)
        pred_img_data = np.zeros_like(image_data)
        for i in indices:
            pred_img_data[tuple(i)] = gmm.predict(image_data[tuple(i)])+1

    else:
        pred_img_data = gmm_predict_map(image_data)

    if keep_best:
        best_ind = df.idxmax()["weight"]
        pred_img_data = pred_img_data==best_ind+1

    return pred_img_data



def main():
    # sklearn_gmm_test()

    gmm_1d_test()

if __name__ == '__main__':
    main()