import numpy as np
import SimpleITK as sitk

"""
references:
https://iopscience.iop.org/article/10.1088/1361-6560/ab2328
https://doi.org/10.1088/1361-6560/ab2328
"""


def normalize_AR(sitk_image, bin_count = 64.0, max_val = 20.0):
    if not isinstance(sitk_image,sitk.Image):
        raise TypeError

    def __AR_scaling__(value):
        return np.round(bin_count/max_val*value)

    vectorized_AR_scaling = np.vectorize(__AR_scaling__)

    np_image = sitk.GetArrayFromImage(sitk_image)
    np_image = vectorized_AR_scaling(np_image)

    out_sitk_image = sitk.GetImageFromArray(np_image)
    out_sitk_image.CopyInformation(sitk_image)
    return sitk_image


def normalize_LAR(sitk_image, bin_count = 64.0):
    if not isinstance(sitk_image,sitk.Image):
        raise TypeError

    np_image = sitk.GetArrayFromImage(sitk_image)
    suv_min = np.min(np_image)

    def __LAR_scaling__(value):
        return (value/np.float(bin_count))-(suv_min*np.float(bin_count))+1.0

    vectorized_AR_scaling = np.vectorize(__LAR_scaling__)
    np_image = vectorized_AR_scaling(np_image)

    out_sitk_image = sitk.GetImageFromArray(np_image)
    out_sitk_image.CopyInformation(sitk_image)
    return sitk_image
