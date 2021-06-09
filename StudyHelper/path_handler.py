#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys, copy
import re
sys.path.insert(0, '/home/fajtai/py/')

from Common.string_functions import *
from Common.CommandRunner.py_io import *

def __str_format__(orig_str, lower = True, remove_spaces = True):
    out_str=orig_str
    if remove_spaces:
        r = re.compile(r"\s+")
        out_str = r.sub("", str(out_str))

    if lower:
        out_str = str(out_str).lower()

    return out_str

def find_sid_n(file_name):
    sid, n = "", None
    file_name = str(file_name)

    r = re.search(r'([A-Za-z][0-9]{3})_([0-9]{2})-', file_name)
    if r:
        if len(r.groups())==2:
            sid = r.group(1)
            n = r.group(2)

        # R = r.group(1)
        # R = R.replace("-","")
        # sid,n = R.split("_")
    else:
        r = re.search(r'[A-Za-z][0-9]{3}-', file_name)
        if r:
            R = r.group(0)
            R = R.replace("-", "")
            sid=R
    return sid,n


def extend_file(path_string,extension):
    return os.path.join(os.path.dirname(path_string), extension + os.path.basename(path_string))

class extendable_file(object):
    def __init__(self, img_path, sid= "", n=None, mod="", **kwargs):
        if isinstance(img_path,extendable_file):
            img_path, sid, n, mod = img_path.s, img_path.sid,img_path.n, img_path.mod

        if not img_path:
            img_path = ""

        if not isinstance(img_path,str):
            img_path = str(img_path)

        self._default_values = [img_path, sid, n, mod]

        self.base_path = os.path.dirname(img_path)
        self.file_name = os.path.basename(img_path)

        if sid =="":
            sid,n= find_sid_n(self.file_name)

        self._sid = sid

        self.n = n
        self._mod = mod

    @staticmethod
    def check_exists_list(*args):
        ex_list = [extendable_file(a) for a in args]
        return all([e.exists() for e in ex_list])


    @property
    def sid(self):
        return self._sid

    @sid.setter
    def sid(self, value):
        self.file_name=self.file_name.replace(self._sid,value)
        self._sid = value


    @property
    def sid_n(self):
        if self.n != None and self.n !="00" and self.n!=0:
            return "{sid}_{n}".format(sid = self.sid,n = self.n)
        else:
            return self.sid

    @property
    def mod(self):
        if self._mod:
            return self._mod
        R = re.search("(.*{0}-)([^.^-]*)".format(self.sid_n),self.file_name)
        if not R:
            return
        if len(R.groups())==2:
            mod = R.group(2)
            self._mod = mod
            return mod

    @mod.setter
    def mod(self, new_mod):
        mod = self.mod
        if mod!= "":
            s_m_o = "{sid_n}-{mod}".format(sid_n=self.sid_n,mod=mod)
            s_m_n = "{sid_n}-{mod}".format(sid_n=self.sid_n,mod=new_mod)
            self.file_name = self.file_name.replace(s_m_o,s_m_n)
        self._mod = new_mod



    @property
    def version(self):
        version = self.file_name.split("{sidn}-{mod}-".format(sidn = self.sid_n, mod = self.mod))
        if len(version)<2:
            return ""
        version = str(version[1]).replace(self.format,"")
        # if "_" in version:
        #     version = version.split("_")[0]

        return version


    @version.setter
    def version(self,new_version):
        old = self.version
        if old: #has version
            self.file_name = self.file_name.replace("{0}-{1}".format(self.mod,old),"{0}-{1}".format(self.mod,new_version))
        else: #has noversion
            self.file_name= self.file_name.replace("{0}".format(self.mod), "{0}-{1}".format(self.mod, new_version))

    @property
    def index(self):
        v = self.version
        index = ""
        if v:
            index = self.file_name.split("{sidn}-{mod}-{version}_".format(sidn=self.sid_n, mod=self.mod,version=v))
            if len(index) < 2:
                return
            index = str(index[-1]).replace(self.format, "")
        return index

    @index.setter
    def index(self, new_index):
        new_index = str(new_index)

        old = self.index
        if old:
            self.file_name = self.file_name.replace("_{0}{1}".format(old,self.format),
                                                    "_{0}{1}".format(new_index,self.format))
        else:
            self.file_name = self.file_name.replace("{0}".format(self.format), "_{0}{1}".format(new_index,self.format))

    @property
    def format(self):
        ext = re.search(r'[.].*', self.file_name)
        if ext != None:
            return ext.group(0)

    @format.setter
    def format(self, value):
        if not str(value).startswith("."):
            value = "."+str(value)
        self.file_name = replace_last_occurrence(self.file_name,self.format,value)

    @property
    def pre_ext(self):
        if self.sid_n == "":
            return ""
        e=self.file_name.split(self.sid_n)
        pre_ext = ""
        if len(e)>1:
            pre_ext = e[0]
        if len(pre_ext)>1:
            return pre_ext[:-1]
        return ""

    @pre_ext.setter
    def pre_ext(self,value):
        if self.sid_n != "":
            e = self.pre_ext
            if e !="":
                e+= "-"
            self.file_name = self.file_name.replace(e,"",1)
        self.__add__(value)

    def gz(self):
        f = self.format
        if ".gz" not in f:
            self.format = f+".gz"
        return self.__str__()

    def ungz(self):
        f = self.format
        self.format = f.replace(".gz","")
        return self.__str__()

    def reset(self):
        self.__init__(*self._default_values)
        return self

    def no_ext(self):
        self.pre_ext= ""
        return self

    def __add__(self, pre_ext):
        if pre_ext != "":
            if self.pre_ext == "":
                self.file_name = "{0}-{1}".format(str(pre_ext), self.file_name)
            else:
                self.file_name = "{0}{1}".format(str(pre_ext), self.file_name)
        return self

    def __mul__(self, temp_pre_ext):
        if self.pre_ext == "":
            p = os.path.join(self.base_path,"{0}-{1}".format(str(temp_pre_ext),self.file_name))
        else:
            p = os.path.join(self.base_path,"{0}{1}".format(str(temp_pre_ext),self.file_name))
        return p

    def modify(self, pre_add=None, format=None):
        fn = self.file_name
        if pre_add:
            if self.pre_ext == "":
                fn = "{0}-{1}".format(str(pre_add), fn)
            else:
                fn = "{0}{1}".format(str(pre_add), fn)

        if format:
            if not format.startswith("."): format = "."+format
            fn = fn.replace(self.format,format)

        return os.path.join(self.base_path,fn)

    def append(self,pre_ext,apply_mod = False):
        if self.pre_ext == "":
            p = os.path.join(self.base_path,"{0}-{1}".format(str(pre_ext),self.file_name))
        else:
            p = os.path.join(self.base_path,"{0}{1}".format(str(pre_ext),self.file_name))
        if apply_mod:
            self.file_name="{0}{1}".format(str(pre_ext),self.file_name)
        return p

    def back_extend(self,back_extension):
        self.file_name=self.file_name.replace(self.format,"{0}{1}".format(back_extension,self.format))
        return self.s

    #base path manipulation

    def change_base(self,new_base_path):
        self.base_path = new_base_path

        return extendable_file(str(self))

    def sim_change_base(self,new_base_path):
        return os.path.join(new_base_path,self.file_name)

    def lower_base(self):
        self.base_path = os.path.dirname(self.base_path)

        return extendable_file(str(self))

    def link_change_base(self,new_base_path, remove_existing = False):
        if os.path.isdir(new_base_path):
            new_full_path = os.path.join(new_base_path, self.file_name)
            py_link(self.s,new_full_path, remove_existing=remove_existing)
            self.change_base(new_base_path)
        return self


    def __str__(self):
        return os.path.join(str(self.base_path),str(self.file_name))

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(str(self))

    @property
    def s(self):
        return self.__str__()

    @property
    def c(self):
        return copy.deepcopy(self)

    def exists(self):
        if not os.path.isfile(self.s):
            printWarning("Warning! File '{0}' not exists!".format(self.s))
            return False
        return True

    def match_substr(self, substr, lower = True, remove_spaces = True):
        fn = __str_format__(self.file_name,lower=lower,remove_spaces=remove_spaces)
        substr = __str_format__(substr,lower=lower,remove_spaces=remove_spaces)

        return substr in fn


    def match_any_list_item(self, substr_list,lower = True, remove_spaces = True):
        fn = __str_format__(self.file_name,lower=lower,remove_spaces=remove_spaces)

        if not isinstance(substr_list,list):
            substr_list = [substr_list]

        substr_list = [__str_format__(s,lower=lower,remove_spaces=remove_spaces) for s in substr_list]

        return any([s in fn for s in substr_list])

    def match_all_list_item(self,substr_list,lower = True, remove_spaces = True):
        fn = __str_format__(self.file_name, lower=lower, remove_spaces=remove_spaces)

        if not isinstance(substr_list, list):
            substr_list = [substr_list]

        substr_list = [__str_format__(s, lower=lower, remove_spaces=remove_spaces) for s in substr_list]

        return all([s in fn for s in substr_list])

    def match_count_list_item(self,substr_list,lower = True, remove_spaces = True):
        fn = __str_format__(self.file_name, lower=lower, remove_spaces=remove_spaces)

        if not isinstance(substr_list, list):
            substr_list = [substr_list]

        substr_list = [__str_format__(s, lower=lower, remove_spaces=remove_spaces) for s in substr_list]

        return sum([s in fn for s in substr_list])

def main():
    pass
    a = extendable_file("/data/epi-norm/e036/t1/c-e036_09-t1-1.30.nii")
    print(a.format)

if __name__ == "__main__":
    main()

