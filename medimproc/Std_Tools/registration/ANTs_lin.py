#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0,'/home/fajtai/py/')

from Std_Tools.common.command_runner import CommandRunner
from Std_Tools.common.command_runner.find_executable import find_executable, find_executable_or_default
from Std_Tools.common.py_io import *

from Std_Tools._package_opts_ import *



def ants_lin_reg(input_img,reference,output_dir="",interp = "Linear", fixed_mask = None, moving_mask = None):
    """
    This function preforms nonlinear registration with ANTs using default recommended options.\n
    :param input: input image
    :param reference: reference image
    :param output_dir: output directory
    :param interp: type of interpolation. ["Linear", "NearestNeighbor", "BSpline order=3"]
    :return: nonlinear transformation file
    """
    if not os.path.isdir(str(output_dir)):
        output_dir = os.path.dirname(str(input_img))

    if interp not in ants_interpList:
        interp = "Linear"

    input_file_name = os.path.basename(str(input_img))

    output_base_path = os.path.join(output_dir,"ants_reg")
    warped=os.path.join(output_dir,"ants_reg-warped.nii")
    i_warped = os.path.join(output_dir,"ants_reg-iwarped.nii")

    if not os.path.exists(str(fixed_mask)):
        fixed_mask = ""

    if not os.path.exists(str(moving_mask)):
        moving_mask = ""

    command = find_executable_or_default("antsRegistration",ants_reg_path) +" --float --collapse-output-transforms 0 --dimensionality 3" \
            " --initial-moving-transform [ {ref}, {input}, 1 ]" \
            " --initialize-transforms-per-stage 0 --interpolation {interp}" \
            " --output [ {output_base}-, {warped}, {iwarped} ] --masks [ {fixed_mask}, {moving_mask} ]".format(ref = str(reference),
                                                                       input=str(input_img), interp=str(interp), output_base=str(output_base_path),
                                                                       warped=str(warped),iwarped=str(i_warped),
                                                                       fixed_mask=str(fixed_mask), moving_mask=str(moving_mask))

    command+= " --transform Rigid[ 0.1 ] --metric Mattes[ {ref}, {input}, 1, 32, Regular, 0.3 ]" \
            " --convergence [ 100000x111100x111100, 1e-08, 20 ] --smoothing-sigmas 4.0x2.0x1.0vox" \
            " --shrink-factors 3x2x1 --use-estimate-learning-rate-once 1 --use-histogram-matching 0 --masks [ {fixed_mask}, {moving_mask} ]".format(ref = str(reference),
                                                                       input=str(input_img), interp=str(interp), output_base=str(output_base_path),
                                                                       warped=str(warped),iwarped=str(i_warped),
                                                                       fixed_mask=str(fixed_mask), moving_mask=str(moving_mask))

    C = CommandRunner()
    C+= command
    C.run()

    py_move(os.path.join(output_dir,warped),os.path.join(output_dir,"aR-{0}".format(input_file_name)))
    py_move(os.path.join(output_dir,i_warped),os.path.join(output_dir,"aR-{0}".format(input_file_name)))
    py_move(output_base_path+"-Composite.h5",os.path.join(output_dir,"trf-aR-{0}".format(input_file_name.replace(".nii",".h5"))))
    py_move(output_base_path+"-InverseComposite.h5",os.path.join(output_dir,"trf-aIR-{0}".format(input_file_name.replace(".nii",".h5"))))

    return os.path.join(output_dir,"trf-aw-{0}".format(input_file_name.replace(".nii",".h5")))


def ants_apply_transform(inNii,  nonlin, outNii,reference, affine="", interp="Linear"):
    """
    This function apply a [linear affine +] nonlinear transformation on the input image\n
    :param inNii: 3D input image
    :param reference: reference image
    :param nonlin: nonlinear transformation in .h5
    :param outNii: output image
    :param affine: affine transformation in txt stored in c3d structure
    :param interp: type of interpolation. ["Linear", "NearestNeighbor", "BSpline order=3"]
    :return: output image
    """
    if interp not in ants_interpList:
        interp = "Linear"

    # image type!
    command = ants_apply_path + \
              " --default-value 0 --float 1" \
              " --input " + str(inNii) + \
              " --input-image-type 0" \
              " --interpolation "+ interp + \
              " --output " + str(outNii) + \
              " --reference-image " + str(reference) + \
              " --transform [ " + str(nonlin) + ", 0 ]"
    if affine != "":
        command += " --transform [ " + str(affine) + ", 0 ]"

    C = CommandRunner()
    C+=[command,str(outNii)]
    C.run()

    return outNii

def ants_apply_label_transform(inNii,  nonlin, outNii,reference, affine="", interp="NearestNeighbor"):
    """
    This function apply a [linear affine +] nonlinear transformation on the input image\n
    :param inNii: 3D input image
    :param reference: reference image
    :param nonlin: nonlinear transformation in .h5
    :param outNii: output image
    :param affine: affine transformation in txt stored in c3d structure
    :param interp: type of interpolation. ["Linear", "NearestNeighbor", "BSpline order=3"]
    :return: output image
    """
    if interp not in ants_interpList:
        interp = "Linear"

    # image type!
    command = ants_apply_path + \
              " --default-value 0 --float 1" \
              " --input " + str(inNii) + \
              " --input-image-type 0" \
              " --interpolation "+ interp + \
              " --output " + str(outNii) + \
              " --reference-image " + str(reference) + \
              " --transform [ " + str(nonlin) + ", 0 ]"
    if affine != "":
        command += " --transform [ " + str(affine) + ", 0 ]"

    C = CommandRunner()
    C+=[command,str(outNii)]
    C.run()

    return outNii

