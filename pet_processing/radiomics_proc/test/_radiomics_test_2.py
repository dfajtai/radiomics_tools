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

dataDir = '/data/dopa-onco/radiomics_test/'
py_mkdirs(dataDir)

logging.raiseExceptions = False

imageName, maskName = getTestCase('brain2', dataDir)
# params = os.path.join(dataDir, "examples", "exampleSettings", "Params.yaml")
# extractor = featureextractor.RadiomicsFeatureExtractor(params)
extractor = featureextractor.RadiomicsFeatureExtractor()
extractor.enableAllFeatures()

# I = sitk.ReadImage(imageName)
# stat_filter = sitk.StatisticsImageFilter()
# stat_filter.Execute(I)
# max_value = stat_filter.GetMaximum()

result = extractor.execute(imageName, maskName, voxelBased= True)
for key, val in six.iteritems(result):
  print("\t%s: %s" %(key, val))

# result = None

# with suppress(Exception):
#   result = extractor.execute(imageName, maskName, voxelBased=True)
#   # result = extractor.execute(imageName, maskName)

result_dict = {}
for key,value in six.iteritems(result):
  if not str(key).startswith("diagnostics"):
    result_dict[key] = value

# for key, val in six.iteritems(result):
#   if isinstance(val, sitk.Image):  # Feature map
#     sitk.WriteImage(val, key + '.nrrd', True)
#     print("Stored feature %s in %s" % (key, key + ".nrrd"))
#   else:  # Diagnostic information
#     print("\t%s: %s" %(key, val))

result_df = pd.DataFrame(pd.Series(dict(result_dict)))
print(result_df)
