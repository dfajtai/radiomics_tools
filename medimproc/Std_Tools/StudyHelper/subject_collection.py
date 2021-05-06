#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys

sys.path.insert(0, '/home/fajtai/py/')

from Common.maskFunctions import *

from Std_Tools.StudyHelper.subject import Subject

from Std_Tools.StudyManager.study_manager import StudyManager as sm_dbh
from Std_Tools.StudyManager.study_settings_loader import get_study_names

from Std_Tools.common.Types.Lists import named_list


class StudySubjects():
    # SubjectDict = {}
    # Subjects = named_list(Subject,key = "ID")
    Subjects = named_list(Subject,key = "sid")

    def __init__(self):

        pass

    @classmethod
    def get_subjects(cls,study_name,T,_id_list = None, *args,**kwargs):
        if not isinstance(T,type):
            raise TypeError("Wrong type! T must be a class.")

        if not study_name in get_study_names():
            raise ValueError("Study '{0}' not defined!".format(study_name))
        cls.study_manager = sm_dbh(study_name)

        # known_sids = cls.study_manager.get_db_ids()

        subjects = cls.study_manager.measurements.read_table()[["sid", "n", "taj", "mdate", "name"]]
        if isinstance(_id_list, list):
            if len(_id_list)>0:
                subjects = subjects[subjects.sid.isin(_id_list)]

        _sid_n = [s.sid_n for s in cls.Subjects]


        for _,series in subjects.iterrows():
            sid = series["sid"]
            n = series["n"]
            kwargs["name"]=series["name"]
            kwargs["taj"]=series["taj"]
            kwargs["mdate"]=series["mdate"]

            S = T(sid,n, *args, **kwargs)
            if S.sid_n not in _sid_n:
                cls.Subjects.append(S)
                _sid_n.append(S.sid_n)

        cls.Subjects.sort(key = lambda x:x.sid_n)

        return cls.Subjects
