#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import pandas as pd

from Std_Tools.common.py_io import py_mkdirs

from Std_Tools.common.colorPrint import *


class realtime_csv():
    def __init__(self, path, header = [], dataframe = None):
        self.path = path
        self.header = header
        if dataframe is None:
            self.dataframe = pd.DataFrame(columns=header)
        else:
            self.dataframe = dataframe


    def create(self,overwrite = False):
        def create_csv():
            if isinstance(self.dataframe, pd.DataFrame):
                self.dataframe.to_csv(self.path, index=None)
            else:
                self.dataframe = pd.DataFrame(columns=self.header)
                self.dataframe.to_csv(self.path, index=None)

        if os.path.exists(str(self.path)):
            if overwrite:
                printWarning("Overwriting existing csv file '{0}'".format(str(self.path)))
                create_csv()
                return

            else:
                printWarning("Extending existing csv file '{0}'".format(str(self.path)))
                self.dataframe = pd.read_csv(self.path)[self.header]
                return



        if not os.path.exists(os.path.dirname(self.path)):
            py_mkdirs(os.path.dirname(self.path))
        create_csv()


    def __add__(self, data):
        if not isinstance(data, pd.DataFrame):
            if not isinstance(data,list):
                data = [data]
            data = pd.DataFrame(data, columns=self.header)
        self.dataframe = self.dataframe.append(data, ignore_index=True)

        with open(self.path, "a") as f:
            data.to_csv(f, header = False, index= None, na_rep="NaN")

        return self