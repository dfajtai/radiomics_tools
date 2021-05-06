#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
import pandas as pd

sys.path.insert(0, '/home/fajtai/py/')

from Std_Tools.StudyHelper.study import Study
from Std_Tools.StudyHelper.modality import Modality
from Std_Tools.StudyHelper.path_handler import extendable_file as ex
from Std_Tools.StudyManager.study_manager import StudyManager, Study
from Std_Tools.common.py_io import py_copy,py_mkdirs,py_link

from Std_Tools.conversion.dcm_nii import dcm_dir_2_niix

from Common.string_functions import *
from Common.colorPrint import *
from Std_Tools.common.unidecode import strcode

class subject_base_files(object):
    def __init__(self):
        self.t1 = None
        self.brain = None
        self.pet = None

        self.ct = None
        self.ct_pet = None

        self.brain_mask = None
        self.warped_brain_mask = None

        self.t2 = None

        self.GM = None
        self.WM = None
        self.warped_GM = None
        self.warped_WM = None

        self.atlas = None
        self.simm_atlas = None


        self.warp_trf = None
        self.lin_trf = None
        self.pet_t1_trf = None
        self.ct_t1_trf = None

        self.r_pet = None #pet image correctly registrated to t1 image


        self.wmparc = None

        self.spm_target_images = []
        self.spm_brain_mask = None


class basic_mods(object):
    def __init__(self,S):
        if isinstance(S,Subject):
            w = S.work_dir
            s = S.source_dir

            self.t1_s = Modality(S.sid,S.n,"t1",os.path.join(s,"t1"))
            self.t1_w = Modality(S.sid,S.n,"t1",os.path.join(w,"t1"))

            self.pet_s = Modality(S.sid, S.n, "pet", os.path.join(s, "pet"))
            self.pet_w = Modality(S.sid, S.n, "pet", os.path.join(w, "pet"))

            self.mrac_s = Modality(S.sid, S.n, "mrac", os.path.join(s, "mrac"))
            self.mrac_w = Modality(S.sid, S.n, "mrac", os.path.join(w, "mrac"))

            self.brain_s = Modality(S.sid, S.n, "brain", os.path.join(s, "brain"))
            self.brain_w = Modality(S.sid, S.n, "brain", os.path.join(w, "brain"))

            self.rfmri_s = Modality(S.sid, S.n, "rfmri", os.path.join(s, "rfmri"))
            self.rfmri_w = Modality(S.sid, S.n, "rfmri", os.path.join(w, "rfmri"))

            self.asl_s = Modality(S.sid, S.n, "asl", os.path.join(s, "asl"))
            self.asl_w = Modality(S.sid, S.n, "asl", os.path.join(w, "asl"))

            self.dti_s = Modality(S.sid, S.n, "dti", os.path.join(s, "dti"))
            self.dti_w = Modality(S.sid, S.n, "dti", os.path.join(w, "dti"))

            self.ct_s = Modality(S.sid, S.n, "ct", os.path.join(s, "ct"))
            self.ct_w = Modality(S.sid, S.n, "ct", os.path.join(w, "ct"))

            self.petct_s = Modality(S.sid, S.n, "petct", os.path.join(s, "petct"))
            self.petct_w = Modality(S.sid, S.n, "petct", os.path.join(w, "petct"))

            self.umap_s = Modality(S.sid,S.n,"umap",os.path.join(s,"umap"))
            self.umap_w = Modality(S.sid,S.n,"umap",os.path.join(w,"umap"))


            self.diff_s = Modality(S.sid, S.n, "diff", os.path.join(s, "diff"))
            self.diff_w = Modality(S.sid, S.n, "diff", os.path.join(w, "diff"))

            self.spm_s = Modality(S.sid, S.n, "spm", os.path.join(s, "spm"))
            self.spm_w = Modality(S.sid, S.n, "spm", os.path.join(w, "spm"))

            self.spm_report = Modality(S.sid, S.n, "spm_report", os.path.join(w,"spm_report"))

            self.t2_s = Modality(S.sid,S.n,"t2",os.path.join(s,"t2"))
            self.t2_w = Modality(S.sid,S.n,"t2",os.path.join(w,"t2"))

            self.angio_s = Modality(S.sid,S.n,"angio",os.path.join(s,"angio"))
            self.angio_w = Modality(S.sid,S.n,"angio",os.path.join(w,"angio"))


class Subject(object):
    n_len = 2

    def __init__(self,sid,n,**kwargs):
        self.study_name = Study.name
        self.sid = strcode(sid)
        self._n = n
        self.base_images = subject_base_files()
        self.mods = basic_mods(self)

        self.name = ""
        if "name" in kwargs.keys():
            self.name = kwargs["name"]

        self.taj = ""
        if "taj" in kwargs.keys():
            self.taj = strcode(kwargs.get("taj"))

        self.mdate = ""
        if "mdate" in kwargs.keys():
            self.mdate = strcode(kwargs.get("mdate"))

    @property
    def sid_n(self):
        if self.n == "00":
            return self.sid
        else:
            return "{0}_{1}".format(self.sid,self.n)

    @property
    def n(self):
        return str(self._n).zfill(Subject.n_len)

    @n.setter
    def n(self, value):
        self._n = int(value)
        self.mods.__init__(self)

    @property
    def work_dir(self):
        p = os.path.join(Study.work_path,self.sid)
        return str(p)

    @property
    def source_dir(self):
        p = os.path.join(Study.source_path, self.sid)
        if os.path.isdir(p):
            return str(p)

    # @property
    def fs_dir(self):
        p = os.path.join(Study.sDir,self.sid_n)
        if os.path.exists(p):
            return str(p)
        printWarning("Freesurfer directory not found for subject {0}".format(self.sid_n))

    def get_mod(self,mod,environment="w",external=""):
        p = ""
        if os.path.isdir(external):
            p = external
        else:
            if environment == "w":
                p = self.work_dir
            if environment == "s":
                p= self.work_dir

        mod_dir = os.path.join(p,mod)
        return Modality(self.sid,self.n,mod,path = mod_dir)


    def make_dir(self):
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

    def get_dcm_for_ext(self,ext_path,overwrite= False):
        if not isinstance(ext_path,ex):
            raise TypeError

        print("Collecting dcm files for '{0}'".format(str(ext_path)))

        s = StudyManager(self.study_name, update=False)

        study_data = s.study_data.read_table()
        subject_data = study_data[(study_data["sid"]==self.sid) & (study_data["n"] == self._n)]

        if len(subject_data) == 0:
            print("Subject not found in StudyDatabase")
            return False

        matching = subject_data[(subject_data["mod"]==ext_path.mod) & (subject_data["version"]==ext_path.version)]
        if len(matching) == 0:
            print("Series not found in StudyDatabase")
            return False

        sd = str(matching.iloc[0]["series_description"]).strip()
        mnc_path = matching.iloc[0]["path"]

        dcm_base_path = os.path.dirname(os.path.dirname(mnc_path))
        if not os.path.isdir(dcm_base_path):
            print("DCM path not exists")
            return False
        dcm_path_csv = os.path.join(dcm_base_path,"dcm-sd-dicoms.csv")

        if not os.path.isfile(dcm_path_csv):
            print("DCM csv not exists")
            return False

        dcm_path_df = pd.read_csv(dcm_path_csv,delimiter=";", header=None)
        dcm_path_df.columns = ["sd","sn","mod","paths"]

        matching_dcms_line = dcm_path_df[dcm_path_df["sd"]==sd]
        if len(matching_dcms_line)==0:
            print("Series description '{0}' not found in csv '{1}'".format(sd,dcm_path_csv))
            return False

        dcm_paths = matching_dcms_line.iloc[0]["paths"]
        dcm_path_list = str(dcm_paths).split(",")

        dcm_count = len(dcm_path_list)
        copy_counter = 0

        out_dcm_dir = os.path.join(self.work_dir,ext_path.mod,"dcm",ext_path.file_name.replace(ext_path.format,""))
        py_mkdirs(out_dcm_dir)

        for dcm in dcm_path_list:
            if os.path.isfile(dcm):
                copy_counter+=1
                out_dcm_path = os.path.join(out_dcm_dir,os.path.basename(dcm))
                py_copy(dcm,out_dcm_path,overwrite=overwrite)

        print("{0} of {1} dcm files of {2} succesfully copied to {3}!".format(str(copy_counter),str(dcm_count),str(ext_path),out_dcm_dir))

        return out_dcm_dir

    def get_dcm_with_sd(self, sd, mod, version,index = 1, convert = True):
        s = StudyManager(self.study_name, update=False)

        study_data = s.study_data.read_table()
        subject_data = study_data[(study_data["sid"]==self.sid) & (study_data["n"] == self._n)]

        if len(subject_data) == 0:
            print("Subject not found in StudyDatabase")
            return False

        mnc_path = subject_data.iloc[0]["path"]

        dcm_base_path = os.path.dirname(os.path.dirname(mnc_path))
        if not os.path.isdir(dcm_base_path):
            print("DCM path not exists")
            return False

        dcm_path_csv = os.path.join(dcm_base_path,"dcm-sd-dicoms.csv")

        dcm_path_df = pd.read_csv(dcm_path_csv,delimiter=";", header=None)
        dcm_path_df.columns = ["sd","sn","mod","paths"]

        matching_dcms_line = dcm_path_df[dcm_path_df["sd"]==sd]
        if len(matching_dcms_line)==0:
            print("Series description '{0}' not found in csv '{1}'".format(sd,dcm_path_csv))
            return False

        dcm_paths = matching_dcms_line.iloc[0]["paths"]
        dcm_path_list = str(dcm_paths).split(",")

        dcm_count = len(dcm_path_list)
        copy_counter = 0

        out_dcm_dir = os.path.join(self.work_dir,mod,"dcm","{0}-{1}-{2}".format(mod,version,index))
        py_mkdirs(out_dcm_dir)

        for dcm in dcm_path_list:
            if os.path.isfile(dcm):
                copy_counter+=1
                out_dcm_path = os.path.join(out_dcm_dir,os.path.basename(dcm))
                py_link(dcm,out_dcm_path)

        print("{0} of {1} dcm files succesfully copied to {2}!".format(str(copy_counter),str(dcm_count),out_dcm_dir))

        if convert:
            out_nii = os.path.join(os.path.join(self.work_dir,mod,"{0}-{1}-{2}-{3}.nii".format(self.sid_n,mod,version,index)))
            dcm_dir_2_niix(out_dcm_dir,out_nii)
            return ex(out_nii)
        else:
            return out_dcm_dir

def main():
    # Study.initWithDB("healing")
    # s = Subject("h013", 1)
    # t1 = s.get_mod("t1","w")
    # s.base_images.t1= t1.get_img("*w*t1*nii")
    #
    # print(s.base_images.t1)
    # if s.base_images.t1: print(s.base_images.t1 + "asc-")
    Study.initWithDB("dopa-onco")
    s = Subject("p008", 2)
    s.get_dcm_for_ext(s.mods.t1_s.get_img("t1-1"))



    pass


if __name__ == "__main__":
    main()

