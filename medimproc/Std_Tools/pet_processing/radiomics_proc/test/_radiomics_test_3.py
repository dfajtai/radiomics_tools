import sys, os, six
import logging
from contextlib import suppress

import radiomics
from radiomics import featureextractor, glrlm, glcm, shape
from radiomics import base
from radiomics import getTestCase

import pandas as pd

import SimpleITK as sitk


from Std_Tools.common.py_io import py_mkdirs

from Std_Tools.pet_processing.radiomics_proc.radiomics_tools3 import extract_radiomics_features

dataDir = '/data/dopa-onco/radiomics_test/'
py_mkdirs(dataDir)

logging.raiseExceptions = False

imageName, maskName = getTestCase('brain2', dataDir)

result_dict = extract_radiomics_features(imageName,maskName,voxel_based=True)

result_df = pd.DataFrame(pd.Series(dict(result_dict)))
print(result_df)
