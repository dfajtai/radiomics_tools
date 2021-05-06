
import radiomics
from radiomics import featureextractor, glrlm, glcm, shape
from radiomics import base

import skimage as sk
import SimpleITK as sitk

from Std_Tools.common.py_io import *
from Std_Tools.common.colorPrint import *
from Std_Tools.img_proc import read_image, NibImg


def radiomics_test():
    img_path = "/data/dopa-onco/p002/pet/S-p002_01-pet-dixon.nii"
    mask_path = "/data/dopa-onco/p002/pet/CL01S-p002_01-pet-dixon.nii"

    # suv_scaling = suv_scaling_values.extract_from_dcm("/data/dopa-onco/p002/pet/dcm/p002_01-pet-dixon.dcm1")
    # print(suv_scaling.bw_factor)

    thr = 5500.0

    I = read_image(img_path)
    mask = I.data>thr

    sitk_img = sitk.ReadImage(img_path)
    # sitk_mask = sitk_img>thr
    sitk_mask = sitk.ReadImage(mask_path)

    # thr_filter = sitk.ThresholdImageFilter()
    # thr_filter.SetLower(5000.0)
    # thr_filter.SetOutsideValue(0)
    # thresholded = thr_filter.Execute(sitk_img)

    shape_params = shape.RadiomicsShape(sitk_img,sitk_mask)
    shape_params.enableAllFeatures()
    print(shape_params.getFeatureNames())

    f_e = featureextractor.RadiomicsFeatureExtractor()
    f_e.enableAllFeatures()
    computed_features = f_e.computeFeatures(sitk_img,sitk_mask,"original")
    print(computed_features.keys())
    vprint_dict(dict(computed_features))

if __name__ == '__main__':
    radiomics_test()
