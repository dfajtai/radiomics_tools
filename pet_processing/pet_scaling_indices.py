#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import numpy as np

sys.path.insert(0,'/home/fajtai/py/')
from Common.CommandRunner import CommandRunner
from Common.colorPrint import *
from Std_Tools.img_proc.IO.img_reader import read_image
from Std_Tools.atlases.freesurfer import gm_from_wmparc, wm_from_wmparc


def get_global_scaling_indices_form_wmparc(wmparc_path,fwhm = 8.0,**kwargs):
    if not os.path.exists(wmparc_path):
        return

    GM = gm_from_wmparc(wmparc_path)
    WM = wm_from_wmparc(wmparc_path)

    GM.smooth(fwhm)
    WM.smooth(fwhm)
    GM_ind = GM.data > 0.4
    WM_ind = WM.data > 0.4

    return np.logical_or(GM_ind, WM_ind).astype("uint8")

def get_global_scaling_indices(gm_mask_path,wm_mask_path,fwhm = 8.0,**kwargs):
    printCommand("Collecting image indices for global scaling...")
    if not CommandRunner.runSwitch:
        return

    GM = read_image(gm_mask_path)
    if not GM:
        return
    WM = read_image(wm_mask_path)
    if not WM:
        return

    GM.smooth(fwhm)
    WM.smooth(fwhm)
    GM_ind = GM.data > 0.4
    WM_ind = WM.data > 0.4

    return np.logical_or(GM_ind, WM_ind).astype("uint8")

def get_gm_indices(gm_mask_path,fwhm = 8.0,**kwargs):
    GM = read_image(gm_mask_path)
    if not GM:
        return
    GM.smooth(fwhm)
    GM_ind = GM.data > 0.4

    return GM_ind.astype("uint8")

def get_proportional_scaling_indices(pet_img_path,brain_mask,mean_factor = 0.8, **kwargd):
    raise NotImplementedError
    #todo jó ez így?!
    pet = read_image(pet_img_path)
    if not pet:
        return

    brain_mask = read_image(brain_mask)
    if not brain_mask:
        return

    m0 = brain_mask.data # csak agyi voxelek...

    mean = np.mean(pet.data)



    return (pet.data>=mean*mean_factor).astype("int")

def main():
    # I = get_global_scaling_indices("/home/fajtai//test/pet_scale/c014-GM-1.nii","/home/fajtai//test/pet_scale/c014-WM-1.nii")
    pass


if __name__ == '__main__':
    main()