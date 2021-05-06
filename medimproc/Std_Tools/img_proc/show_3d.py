#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.animation as manim
import numpy as np

# from mayavi import mlab

import os, sys

sys.path.insert(0, '/home/fajtai/py/')


# def show_data_in_3d(data,contours=0.5):
#
#     src = mlab.pipeline.scalar_field(data.astype(np.float))
#     if not isinstance(contours,list):
#         contours=[contours]
#     mlab.pipeline.iso_surface(src, contours=contours, opacity=0.5)
#     mlab.show()

def z_slicedump_gif(data,low, high,output_file,fps = 10):
    nz = data.shape[2]

    fig = plt.figure(figsize=(3, 3))
    ax = fig.add_subplot(111)
    img = ax.imshow(data[:, :, 0], vmin=low, vmax=high,
                    cmap=plt.cm.gray,
                    interpolation='bilinear')

    writer = manim.ImageMagickWriter(fps=fps)

    with writer.saving(fig, output_file, 100):
        for i in range(nz):
            img.set_data(data[:, :, i])
            ax.set_title("%02d" % i)
            writer.grab_frame()

def main():
    pass


if __name__ == '__main__':
    main()