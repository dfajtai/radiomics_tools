#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Short explanation"""

from datetime import datetime as DT

import os, sys
import math
from datetime import datetime as dtime
import pydicom as dicom
import numpy as np


sys.path.insert(0, '/home/fajtai/py/')

class suv_scaling_values(object):
    def __init__(self,  sex="",weight=1,height=1,inj_dose=1,t0=None,t1=None, units = "BQML", *args,**kwarsg):
        self.sex = sex
        self.weight = weight
        self.height = height
        self.inj_dose = inj_dose
        self.t0 = t0 # injection time
        self.t1 = t1 # series time
        self.units = units


    @staticmethod
    def extract_from_dcm(dcm_path):
        if not os.path.isfile(dcm_path):
            print("dcm file '{0}' not exists".format(str(dcm_path)))
            return False

        try:
            d = dicom.read_file(dcm_path)

            dcm_suv_info = {}
            dcm_suv_info["sex"] = d.PatientSex
            dcm_suv_info["weight"] = d.PatientWeight  # kg
            dcm_suv_info["height"] = d.PatientSize * 100  # cm
            dcm_suv_info["inj_dose"] = np.float((d[0x0054, 0x0016][0][0x0018, 0x1074]).value)  # .astype('float32')
            dcm_suv_info["t0"] = DT.strptime((d[0x0054, 0x0016][0][0x0018, 0x1072]).value,"%H%M%S.%f")  # injection time
            dcm_suv_info["t1"] = DT.strptime((d[0x0008, 0x0031].value), "%H%M%S.%f")  # accepted_series time
            dcm_suv_info["units"] = d[0x0054,0x1001].value

            return suv_scaling_values(**dcm_suv_info)

        except Exception as e:
            print("Error during suv data extraction from '{0}'.".format(dcm_path))
            raise e



    @property
    def dt_s(self):
        dt = self.t1-self.t0
        dt_s = dt.total_seconds()
        return dt_s


    @property
    def bw_factor(self):
        return self._dose_factor_ * self.weight*1000.0

    @property
    def bsa_factor(self):
        return self._dose_factor_ * self.weight**(0.425)*self.height**(0.725)*71.84

    @property
    def lbm_factor(self):
        if self.sex =="M":
            return self._dose_factor_ * (1.1*self.weight-128.0*(self.weight/self.height)**2.0)*1000
        else:
            return self._dose_factor_* (1.07 * self.weight- 148.0 * (self.weight/ self.height) ** 2.0)*1000

    @property
    def _kBq_unit_scaling_factor_(self):
        if self.units == "BQML":
            return 1e-3
        else:
            return 1

    @property
    def _f18_decay_factor_(self):
        T = 6586.2
        return math.exp(- self.dt_s * (math.log(2) / T))

    @property
    def _dose_factor_(self):
        # ! VALIDATED !
        return 1.0/(self.inj_dose*self._f18_decay_factor_)


def main():
    i = suv_scaling_values.extract_from_dcm("/data/dopa-onco/p008/pet/dcm/p008_01-pet-dixon.dcm1")
    print(i.bw_factor)
    print("done")

if __name__ == '__main__':
    main()
