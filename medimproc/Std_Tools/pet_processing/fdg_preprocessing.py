#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from Common.CommandRunner.py_io import py_remove

from .pet_crop import pet_box_crop,pet_box,fdg_brain_mask
from Std_Tools import extendable_file as ex
from Std_Tools.img_proc.preprocessing import *
from Std_Tools.registration import *

# def pet_2_t1_with_mrac(pet,t1,mrac):
#     pet = ex(pet)
#     t1 = ex(t1)
#     mrac = ex(mrac)
#
#     l_mrac = mrac*"l"
#     mri_convert_resample(l_mrac, pet.s)
#
#     r_mrac = mrac*"r0"
#     mrac_2_t1_trf = mrac.modify("trf-r0",".mat")
#     flirt_register(l_mrac,t1,mrac_2_t1_trf,r_mrac,6,cost="normmi")
#
#     r0_pet = pet * "r0"
#     flirt_apply_xfm(pet.s, t1, mrac_2_t1_trf, r0_pet)
#
#     # sr0_pet = pet*"sr0"
#     # flirt_resample(r0_pet,sr0_pet,1)
#
#     cr0_pet = pet * "cr0"
#     pet_box_crop(r0_pet, cr0_pet, pet_box(r0_pet, fdg_brain_mask))
#
#     r_pet = pet + "rc"
#     trf_r0_pet_2_t1 = pet.modify("trf-r-cr0", ".mat")
#     flirt_register(cr0_pet, t1, trf_r0_pet_2_t1, r_pet, dof=6, search=[-5, 5], cost="corratio")
#
#     return r_pet

def dyn_pet_preproc(dyn_pet_input,mc_avg_pet_out):
    dyn_pet_input = ex(dyn_pet_input)
    mc_avg_pet_out=ex(mc_avg_pet_out).s
    if not dyn_pet_input.exists():
        return

    mc = dyn_pet_input*"mc"
    motion_corr(dyn_pet_input,mc)
    time_mean(mc,mc_avg_pet_out)
    py_remove(mc)

    return True