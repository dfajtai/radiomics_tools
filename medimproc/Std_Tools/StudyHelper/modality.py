#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys

sys.path.insert(0, '/home/fajtai/py/')

from .path_handler import extendable_file as ex
from Common.CommandRunner.py_io import *

class Modality(object):
    def __init__(self, sid,n,mod,path=""):
        self.sid, self.n, self.mod = sid, n, mod

        self.base_path = path

        self.base_file = ""
        self.reg_trf = ""
        self.lin_trf = ""
        self.warp = ""

        self.imgs = []

    @property
    def sid_n(self):
        return "{0}_{1}".format(self.sid,str(self.n).zfill(2))

    def get_img(self,file_name_part, subdir = "", shortest_match=True, set_default = False, match_sid_n = True):
        p = os.path.join(self.base_path,subdir)
        if not os.path.isdir(p):
            printWarning("Directory '{0}' not exits!".format(str(p)))
            return ex(None)

        files = os.listdir(p)
        base_file_name_part = str(file_name_part).split("*")
        match = [f for f in files if all([m in f for m in base_file_name_part])]

        if match_sid_n:
            match = [f for f in match if self.sid_n in str(f)]

        match_p = [os.path.join(p,m) for m in match if m !=""]
        if len(match_p)==0:
            printWarning("File not found in directory '{0}' with mask '{1}'!".format(str(p),file_name_part))
            return ex(None)

        if shortest_match:
            match_p = sorted(match_p, key=lambda x:len(x))[0]
        else:
            match_p= sorted(match_p)[0]

        if set_default:
            self.base_file = ex(match_p,self.sid,self.n,self.mod).s

        return ex(match_p,self.sid,self.n,self.mod)

    def get_imgs(self,file_name_part,subdir = "",all_shortest = True, D = 0, match_sid_n = True):
        p = os.path.join(self.base_path, subdir)
        if not os.path.isdir(p):
            printWarning("Directory '{0}' not exits!".format(str(p)))
            return

        all_files = os.listdir(p)
        if not isinstance(file_name_part,list):
            file_name_part= [file_name_part]

        matching_files = []

        for fn_part in file_name_part:
            base_file_name_part = str(fn_part).split("*")
            match = [f for f in all_files if all([m in f for m in base_file_name_part])]

            if match_sid_n:
                match = [f for f in match if self.sid_n in str(f)]

            match_p = [os.path.join(p, m) for m in match if m != ""]
            if len(match_p) == 0:
                printWarning("File not found in directory '{0}' with mask '{1}'!".format(str(p),fn_part))
                continue

            match_p = sorted(match_p, key=lambda x: len(x))
            min_len = len(match_p[0])

            if all_shortest:
                match_p = [mp for mp in match_p if (len(mp)>=min_len-D and len(mp)<=min_len+D)]

            files = [ex(mp,self.sid,self.n,self.mod) for mp in match_p]
            matching_files.extend(files)
        return matching_files

    def get_imgs_with_pre(self,pre_ext_parts,subdir = "", all_shortest = True, match_sid_n = True):
        p = os.path.join(self.base_path, subdir)
        if not os.path.isdir(p):
            printWarning("Directory '{0}' not exits!".format(str(p)))
            return

        files = os.listdir(p)
        _pre_ext_parts = str(pre_ext_parts).split("*")
        match = [f for f in files if all([m in str(ex(f).pre_ext) for m in _pre_ext_parts])]

        if match_sid_n:
            match = [f for f in match if self.sid_n in str(f)]

        match_p = [os.path.join(p, m) for m in match if m != ""]
        if len(match_p) == 0:
            printWarning("File not found in directory '{0}' with pre_ext '{1}'!".format(str(p), pre_ext_parts))
            return

        match_p = sorted(match_p, key=lambda x: len(ex(x).pre_ext))
        min_len = len(ex(match_p[0]).pre_ext)

        if all_shortest:
            match_p = [mp for mp in match_p if len(ex(mp).pre_ext) == min_len]

        files = [ex(mp, self.sid, self.n, self.mod) for mp in match_p]
        files = [f for f in files if os.path.isfile(str(f))]
        return files


    def get_imgs_without_pre(self, format = ".nii", match_sid_n=True):
        p = os.path.join(self.base_path)
        if not os.path.isdir(p):
            printWarning("Directory '{0}' not exits!".format(str(p)))
            return

        files = os.listdir(p)
        files = [f for f in files if ex(f).format==format]

        if match_sid_n:
            files = [f for f in files if self.sid_n in str(f)]

        files = [os.path.join(self.base_path,f) for f in files]
        return files

    def create_dir(self):
        d = os.path.join(self.base_path)
        if not os.path.exists(d):
            os.makedirs(d,0o775)
        return self

    @property
    def s(self):
        return self.base_path

    def get_img_with_version_and_fix_pre(self, version, pre = "", shortest = True, match_sid_n = True):
        p = os.path.join(self.base_path)
        if not os.path.isdir(p):
            printWarning("Directory '{0}' not exits!".format(str(p)))
            return

        files = os.listdir(p)
        version_parts = str(version).split("*")

        if match_sid_n:
            files = [f for f in files if self.sid_n in str(f)]

        files = filter(lambda x: all([str(vp) in x for vp in version_parts]) and ex(x).pre_ext == pre,files)

        if len(files)==0:
            return

        files = sorted(files, key=lambda x: len(ex(x).version))
        if shortest:
            return ex(os.path.join(p,files[0]))
        else:
            return [ex(os.path.join(p,f)) for f in files]

def main():
    pass


if __name__ == "__main__":
    main()
