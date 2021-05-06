#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
from shutil import copyfile,rmtree
import zipfile
from datetime import datetime

import unicodedata
import re

sys.path.insert(0, '/home/fajtai/py/')

from Std_Tools.common.list_functions import *
from Std_Tools.common.command_runner.command_runner import CommandRunner
from Std_Tools.common.colorPrint import *
from Std_Tools.common.list_functions import unwrapList

from Std_Tools.common.string_handling import hun2ascii_remove_spec


class FileNotExistsError(Exception):
    def __init__(self, *files):
        self.message="Warning! Some crucial file are missing!"
        super(FileNotExistsError,self).__init__(self.message)
        self._missing_files = [str(f) for f in files if not os.path.exists(str(f))]


    @property
    def missing_files(self):
        return "{message}\n{files}".format(message=self.message,files=", ".join(self._missing_files))

def py_copy(source,target,overwrite = False):
    source = str(source)
    target = str(target)

    if source == target:
        return
    if os.path.exists(source):
        if os.path.exists(target) and (CommandRunner.overwrite == False and overwrite == False):
            printWarning("File {0} already exists!".format(str(target)))
            return
        if CommandRunner.runSwitch:
            printCommand("Copying {0} -> {1} ...".format(str(source),str(target)))
            copyfile(source,target)
        else:
            printExtra("Copying {0} -> {1} ...".format(str(source),str(target)))

def py_move(source,target,overwrite = False):
    source = str(source)
    target = str(target)

    if source == target:
        return
    if os.path.exists(source):
        if os.path.exists(target) and CommandRunner.overwrite == False and overwrite == False:
            printWarning("File {0} already exists!".format(str(target)))
            return
        if CommandRunner.runSwitch:
            printCommand("Moving {0} -> {1} ...".format(str(source),str(target)))
            os.rename(source,target)
        else:
            printExtra("Moving {0} -> {1} ...".format(str(source),str(target)))

def py_link(source,target,remove_existing= True):
    source = str(source)
    target = str(target)

    if source == target:
        return
    if os.path.exists(source):
        if os.path.exists(target) and CommandRunner.overwrite == False:
            printWarning("File {0} already exists!".format(str(target)))
            return
        if os.path.exists(str(target)) and remove_existing:
            os.remove(str(target))
        if CommandRunner.runSwitch:
            printCommand("Linking {0} -> {1} ...".format(str(source),str(target)))
            os.symlink(str(source),str(target))
        else:
            printExtra("Linking {0} -> {1} ...".format(str(source),str(target)))

def py_remove(*target):
    if not isinstance(target,list):
        target = [target]

    target = unwrapList(target)

    for t in target:
        if not os.path.exists(t):
            continue
        else:
            if CommandRunner.runSwitch:
                os.remove(t)
            printExtra("Removing {0}".format(str(t)))

def py_rm_tree(target,allow_root=False):
    if not os.path.exists(str(target)):
        return

    else:
        s = str(target).split("/")
        if len(s)<=2 and not allow_root:
            printWarning("Tree remove not allowed on root level directory!")

        else:
            if CommandRunner.runSwitch:
                printCommand("Removing {0}/ ...".format(str(target)))
                rmtree(str(target), ignore_errors=True)
            else:
                printExtra("Removing {0}/ ...".format(str(target)))


def py_mkdirs(*dirs):
    if not isinstance(dirs,list):
        dirs = [dirs]

    dirs = unwrapList(dirs)

    for d in dirs:
        if not os.path.isdir(d):
            if CommandRunner.runSwitch:
                printCommand("Creating directory {0}...".format(str(d)))
                os.makedirs(d, 0o775)
            else:
                printExtra("Creating directory {0}...".format(str(d)))


def normalize_path(input_path):
    normalized = "/".join(hun2ascii_remove_spec(part,allowed_chars=[".","-","_"]) for part in str(input_path).split("/"))
    return normalized


def py_zip_decompress(zip_path, out_path, recursive = False, add_folder = False, extension_filter_list = None, normalize = True):
    decompressed_paths = []

    if add_folder:
        out_path = os.path.join(out_path,os.path.basename(os.path.splitext(zip_path)[0]))
        py_mkdirs(out_path)

    try:
        if recursive:
            with zipfile.ZipFile(zip_path,'r') as zip_ref:
                for f in zip_ref.namelist():
                    # print(f)
                    if os.path.splitext(f)[1]==".zip":
                        sub_path = os.path.join(out_path,os.path.splitext(f)[0])
                        py_mkdirs(sub_path)
                        zip_ref.extract(f,out_path)
                        B = os.path.basename(f)
                        sub_zip_path = os.path.join(os.path.dirname(sub_path),B)
                        sub_decompressed =  py_zip_decompress(sub_zip_path,sub_path, recursive=recursive,add_folder=False)
                        decompressed_paths.extend(sub_decompressed)
                        py_remove(sub_zip_path)
                    else:
                        if isinstance(extension_filter_list,list):
                            out_ext = os.path.splitext(f)[1]

                            if out_ext in extension_filter_list or str(f).endswith("/"):
                                zip_ref.extract(f, out_path)
                                decompressed_path = os.path.join(out_path,f)
                                if normalize:
                                    py_move(decompressed_path,normalize_path(decompressed_path))
                                    decompressed_path = normalize_path(decompressed_path)
                                decompressed_paths.append(decompressed_path)
                        else:
                            zip_ref.extract(f,out_path)
                            decompressed_path = os.path.join(out_path, f)
                            if normalize:
                                py_move(decompressed_path, normalize_path(decompressed_path))
                                decompressed_path = normalize_path(decompressed_path)
                            decompressed_paths.append(decompressed_path)


        else:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(out_path)
                for f in zip_ref.namelist():
                    decompressed_paths.append(os.path.join(out_path, f))

    except Exception as e:
        print(e.__str__())
        raise e

    finally:
        return decompressed_paths


def check_path_dict(raise_exception = False,**paths):
    check_list = []
    out_list = []
    not_existing_files = []
    for k in paths.keys():
        path = paths[k]
        exists = False
        if isinstance(path,list):
            exists = any([os.path.exists(str(p)) for p in path])
        else:
            exists = os.path.exists(str(path))

        check_list.append(["{0} = ".format(k),"'{0}'".format(path),"[ OK ]" if exists else "[    ]"])
        out_list.append(exists)
        if not exists:
            not_existing_files.append(path)

    vprint(check_list)
    if not raise_exception:
        return out_list

    if not all(out_list):
        raise FileNotExistsError(*not_existing_files)


def get_subdirs(path,mask = None):
    if not os.path.isdir(path):
        return []

    L = filter(lambda x: os.path.isdir(str(x)), [os.path.join(path,_d) for _d in os.listdir(path)])
    if mask:
        L = filter(lambda x: all([m in os.path.basename(x) for m in str(mask).split("*")]), L)

    return L

def replace_in_file(text_file, renameDict):
    if not os.path.exists(text_file):
        printError("Error! File not exists '{0}'!".format(text_file))
        return
    with open(text_file, 'r') as f:
        data = f.readlines()
    for k in renameDict:
        data = map(lambda x: x.replace(k, renameDict[k]), data)

    with open(text_file, "w") as f:
        f.writelines(data)


def file_checkout(target_file,daily = False):
    if not os.path.exists(target_file):
        return

    printInfo("Create checkout for '{0}'".format(target_file))

    try:
        file_timestamp = os.path.getmtime(target_file)
        file_date_time = datetime.fromtimestamp(file_timestamp)
        file_date = file_date_time.strftime("%Y%m%d")

        _new_file_name = "_{0}".format(file_date).join(os.path.splitext(target_file))

        if os.path.exists(_new_file_name):
            if not daily:
                file_date_time_str = file_date_time.strftime("%Y%m%d_%H%M")
                _new_file_name = "_{0}".format(file_date_time_str).join(os.path.splitext(target_file))

        py_copy(target_file,_new_file_name,overwrite=True)

    except:
        return

if __name__ == '__main__':
    # file_checkout("/home/fajtai/timestamp_test",daily=True)

    # py_zip_decompress('/home/fajtai/test/zip_test/asd_2.zip', "/home/fajtai/test/zip_test",True)
    py_zip_decompress('/home/fajtai/test/zip_test/zt2.zip', "/home/fajtai/test/zip_test",True, extension_filter_list=[".txt"])
    pass
