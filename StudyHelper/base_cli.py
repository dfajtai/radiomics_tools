#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
from optparse import OptionParser, OptionGroup
import re
import math
import pandas as pd
# from types import NoneType
NoneType = type(None)

sys.path.insert(0, '/home/fajtai/py/')

from Std_Tools.common.command_runner import CommandRunner
from Std_Tools.common.colorPrint import *
from Std_Tools.StudyManager.study_manager import StudyManager as SM
from Std_Tools.StudyManager.study_settings_loader import get_study_names

from Std_Tools.common.unidecode import unidecode, strcode

def _csv_sid_list_extract(sid_csv_path):
    if not os.path.exists(sid_csv_path):
        return []

    sid_list = []
    try:
        df = pd.read_csv(sid_csv_path)
        if 'sid' in df.columns:
            df = df[['sid']]
            df = df.dropna()
            sid_list = list(df["sid"])
    except:
        return []

    return sid_list

class OptionParsingError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg

class OptionParsingExit(Exception):
    def __init__(self, status, msg):
        self.msg = msg
        self.status = status

class ModifiedOptionParser(OptionParser):
    def error(self, msg):
        # OptionParser.print_usage(self)
        OptionParser.print_help(self)
        printError("\nError! Wrong option or value!")
        print(bcolors.Red+bcolors.BOLD)
        OptionParser.error(self,msg)
        # raise OptionParsingError(msg)

    def exit(self, status=0, msg=None):
        OptionParser.exit(self,status,msg)
        # raise OptionParsingExit(status, msg)

    def print_help(self, file=None):
        OptionParser.print_help(self,file = file)
        sys.exit()

class base_cli(object):
    def __init__(self,study_name,*args,**kwargs):
        super(base_cli, self).__init__()
        _study_names = get_study_names()
        study_name = strcode(study_name)
        if not study_name in _study_names:
            raise ValueError("Study '{0}' not defined!".format(study_name))
        self.study_manager = SM(study_name)

        self.IDs = []
        self.n_s = []
        self.all_sid = self.all_n = False
        self.sim = self.overwrite = False
        self.group = ""
        self.start = 0
        self.end = 999

        self.modulo = ""

        self.sid_csv = ""

        keys = kwargs.keys()
        if "IDs" in keys: self.IDs = kwargs["IDs"]
        if "all_sid" in keys: self.all_sid = kwargs["all_sid"]

        if "n_s" in keys: self.n_s = kwargs["n_s"]
        if "all_n" in keys: self.all_n = kwargs["all_n"]

        if "start_index" in keys: self.start = kwargs["start_index"]
        if "end_index" in keys: self.end = kwargs["end_index"]
        if "group" in keys: self.group = kwargs["group"]

        if "sim" in keys: self.sim = kwargs["sim"]
        CommandRunner.runSwitch = not self.sim
        if "overwrite" in keys: self.overwrite = kwargs["overwrite"]
        CommandRunner.overwrite = self.overwrite

        if "info" in keys: self.info = kwargs["info"]

        if "modulo" in keys: self.modulo = kwargs["modulo"]

        self.sid_csv = kwargs.get("sid_csv")

    def print_info(self,**kwargs):

        if kwargs.get("summary"):
            raise NotImplementedError

    def id_collect(self):
        return self._manual_id_collect(self.IDs, self.all_sid, self.start, self.end, self.group, self.modulo)

    def n_filtering(self,known_n_for_subject):
        if self.all_n:
            return known_n_for_subject
        else:
            return [n for n in known_n_for_subject if n in self.n_s]

    def _manual_id_collect(self, IDs, all_sid, start, end, group, modulo = ""):

        if isinstance(IDs, list):
            _ids = IDs[:]
        else:
            _ids = str(IDs).replace(" ", "").split(",")

        if isinstance(self.sid_csv,str):
            if self.sid_csv!="":
                _ids = _csv_sid_list_extract(self.sid_csv)

        known_sid_s = self.study_manager.get_id_list()

        if all_sid:
            _ids = known_sid_s[:]
        else:
            unknown = list(set(_ids).difference(set(known_sid_s)))
            if len(unknown) > 0 and _ids != [""]:
                printInfo("The following measurements are unknown for StudyManager:")
                printInfo(", ".join(unknown))

            _ids = list(set(known_sid_s).intersection(set(_ids)))

        if isinstance(group,str):
            if group != "":
                groups = str(group).split(',')
                _ids = [i for i in _ids if any([str(i).startswith(g) for g in groups])]

        nums = [int(re.sub("[^0-9]", "", str(i))) for i in _ids]

        if modulo != "":
            N = int(modulo.split(":")[0])
            M = int(modulo.split(":")[1])
            IDs = [i for i, n in zip(_ids, nums) if n >= start and n <= end and n % N == M ]
        else:
            IDs = [i for i, n in zip(_ids, nums) if n >= start and n <= end]

        return IDs


    @staticmethod
    def append_parser(parser):
        if not isinstance(parser,OptionParser):
            raise TypeError("Wrong type. Only OptionParser allowed!")

        # basic
        basic_options = OptionGroup(parser, "Basic options",
                                    "In this section you can define target measurements in the given study")
        basic_options.add_option("-i", "--id", type="string", dest="IDs",
                                 help="Target ID, or IDs in STUDY directory. To define multiple subject, please separate object IDs with ','.\n",
                                 default="")

        basic_options.add_option("-a", "--all", dest="all_sid",
                                 help="Include if you want to compute all subject.\n Mask is setted in study.py",
                                 default=False,
                                 action="store_true")

        basic_options.add_option("-n", type="string", dest="n", help="Target measurement indexes [n1,n2,...]",
                                 default="1")

        basic_options.add_option("-A", "--alln", dest="all_n",
                                 help="Include if you want to compute all measurement for selected measurements.\n Mask is setted in study.py",
                                 default=False, action="store_true")

        basic_options.add_option("--from", type="int", dest="start_index",
                                 help="This parameter filters IDs by index. Only index>f patients will be computed.",
                                 default=0)
        basic_options.add_option("--to", type="int", dest="end_index",
                                 help="This parameter filters IDs by index. Only index<=t patients will be computed.",
                                 default=999)

        basic_options.add_option("-g", "--group", type="string", dest="group",
                                 help="Use this parameter to define target subject groups (etc e,c,p,...). In default, every group handled the same way.",
                                 default="")

        basic_options.add_option("--modulo", type="string", dest="modulo",
                                 help="This parameter filters IDs by index with modulo and remainder deifined with an 'N:M' format string, where N is the divider and M is the remainder."
                                      "Only index mod N = M patients will be computed.", default="")


        basic_options.add_option("--sid_csv", type="string", dest="sid_csv",
                                 help="With this parameter, you can use a csv for target sid selection.\nCSV format: sid = columns['sid']",
                                 default="")

        expert_settings = OptionGroup(parser, "Expert settings", "In this section you can modify expert attributes of the pipeline, like simulation and unlocking overwrite protection, etc...")
        expert_settings.add_option("--sim", dest="simulate", help="Include if you want to simulate all computation and processes.\n", default=False, action="store_true")
        expert_settings.add_option("-O","--overwrite", dest="overwrite", help="Include if you want to allow overwriting existing files.\n", default=False, action="store_true")
        expert_settings.add_option("--info", dest="info",
                                   help="Include if you want to get basic information about the study.\n", default=False,
                                   action="store_true")
        parser.add_option_group(basic_options)
        parser.add_option_group(expert_settings)

        return parser


    @staticmethod
    def read_input(parser,T,study_name=None):
        if not isinstance(parser,OptionParser):
            raise TypeError("Wrong type. Only OptionParser allowed!")
        if not isinstance(T,type):
            return
        try:
            (opt, args) = parser.parse_args()
        except:
            print(bcolors.Default + bcolors.ENDC)
            sys.exit()

        kwargs = opt.__dict__.copy()
        _IDs = opt.IDs
        kwargs["IDs"] = str(_IDs).replace(" ", "").split(",")
        kwargs["all_sid"] = opt.all_sid

        n = opt.n
        n_s = str(n).replace(" ", "").split(",")
        if n_s == [""]: n_s = []
        kwargs["n_s"] = [str(int(n)).zfill(2) for n in n_s]
        kwargs["all_n"] = opt.all_n

        kwargs["start_index"] = opt.start_index
        kwargs["end_index"] = opt.end_index
        kwargs["group"] = opt.group

        kwargs["sim"] = opt.simulate
        kwargs["overwrite"] = opt.overwrite

        kwargs["modulo"] = opt.modulo

        kwargs["sid_csv"] = opt.sid_csv

        # additional_kwargs = dict([(k,opt.__dict__[k]) for k in opt.__dict__.keys() if k not in kwargs.keys()])


        if not isinstance(study_name,NoneType):
            return T(study_name = study_name, **kwargs)

        else:
            return T(**kwargs)
