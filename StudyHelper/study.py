#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'/home/fajtai/py/')
from Common.colorPrint import *

from Std_Tools.StudyManager.study_settings_loader import study_settings_db
from Std_Tools.common.Types.Lists import named_list

from Std_Tools.common.unidecode import strcode,unidecode

class Study(object):
    """
    This class stands for easily get subject paths in different environments.
    """
    name = ""
    source_path = None
    work_path = None
    sid_mask = None
    dicom_path = None
    study_db = None # new study_manager
    study_csv = None # old time study_manager
    sDir = None
    study_xls = None

    csvHandler=None

    @classmethod
    def clsInit(cls,name,source_path, work_path, sid_mask="p001", dicom_path=None, study_db=None, sDir = None, study_xls = None, study_csv = None,**kwargs):
        cls.name = strcode(name)
        cls.source_path = strcode(source_path)
        cls.work_path = strcode(work_path)
        cls.sid_mask = strcode(sid_mask)
        cls.dicom_path = strcode(dicom_path)
        cls.study_db = strcode(study_db)
        cls.study_csv = strcode(study_csv)
        cls.sDir = strcode(sDir)
        cls.study_xls = strcode(study_xls)

        # cls.csvHandler = StudyCSVHandler(studyCsv,dicomPath)

    def __init__(self,name,source_path, work_path, sid_mask="p001", dicom_path=None, study_db=None, sDir = None, study_xls = None, study_csv = None,**kwargs):
        self.name = strcode(name)
        self.source_path = strcode(source_path)
        self.work_path = strcode(work_path)
        self.sid_mask = strcode(sid_mask)
        self.dicom_path = strcode(dicom_path)
        self.study_db = strcode(study_db)
        self.study_csv = strcode(study_csv)
        self.sDir = strcode(sDir)
        self.study_xls = strcode(study_xls)

    @classmethod
    def initWithDB(cls, name):
        """initialize study with database"""

        sdh = study_settings_db(study_settings_db.study_def_db_path)
        study_db = sdh.read_table()
        cls.study_db=study_db

        study_list = list(study_db["name"])

        name=unidecode(name)

        if name in study_list:
            study_def = study_db[study_db["name"]==name]
            study_def.reset_index(drop=True,inplace=True)
            study_def =  study_def.to_dict("records")[0]
            cls.clsInit(**study_def)
        else:
            printError("Error! Study '{0}' not defined in '{1}'.".format(name,study_settings_db.study_def_db_path))
            sys.exit()

    @classmethod
    def init_all(cls):
        pass


    @classmethod
    def to_dict(cls):
        D = {}
        D["name"] = cls.name
        D["source_path"] = cls.source_path
        D["work_path"] = cls.work_path
        D["sid_mask"] = cls.sid_mask
        D["dicom_path"] = cls.dicom_path
        D["study_db"] = cls.study_db
        D["study_csv"] = cls.study_csv
        D["sDir"] = cls.sDir
        D["study_xls"] = cls.study_xls

        return D
    
    def __str__(self):
        D = {}
        D["name"] = self.name
        D["source_path"] = self.source_path
        D["work_path"] = self.work_path
        D["sid_mask"] = self.sid_mask
        D["dicom_path"] = self.dicom_path
        D["study_db"] = self.study_db
        D["study_csv"] = self.study_csv
        D["sDir"] = self.sDir
        D["study_xls"] = self.study_xls

        return str(D)


class StudyCollection():
    Studies = named_list(Study, key="name")
    def __init__(self):
        pass

    @classmethod
    def get_all_study(cls):
        sdh = study_settings_db(study_settings_db.study_def_db_path)
        study_db = sdh.read_table()

        study_list = list(study_db["name"])

        for name in study_list:
            study_def = study_db[study_db["name"] == name]
            study_def.reset_index(drop=True, inplace=True)
            study_def = study_def.to_dict("records")[0]
            cls.Studies.append(Study(**study_def))

    @classmethod
    def get_study(cls,name):
        StudyCollection.get_all_study()
        try:
            s = StudyCollection.Studies[name]
            return s
        except IndexError:
            print("Study with name '{0}' not defined!".format(name))

