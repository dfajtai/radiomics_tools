#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, datetime
import os,sys
from optparse import OptionParser
import subprocess


sys.path.insert(0, '/home/fajtai/py/')
from Std_Tools.common.colorPrint import *
from Std_Tools.common.MyTime import *
from Std_Tools.common.list_functions import *

def temp_run(func):
    def func_wrapper(*args,**kwargs):
        rs = CommandRunner.runSwitch
        CommandRunner.runSwitch = True
        return_val =  func(*args,**kwargs)
        CommandRunner.runSwitch = rs
        return return_val

    return func_wrapper

def temp_sim(func):
    def func_wrapper(*args,**kwargs):
        rs = CommandRunner.runSwitch
        CommandRunner.runSwitch = False
        return_val =  func(*args,**kwargs)
        CommandRunner.runSwitch = rs
        return return_val

    return func_wrapper

class CommandList(list):
    def __new__(cls, data=None):
        if not data:
            data = []

        if not isinstance(data,list):
            data = [data]

        data = [Command(d) for d in data]

        obj = super(CommandList, cls).__new__(cls, data)
        return obj

    def __str__(self):
        return vprint(self)

    def __add__(self, other):
        return CommandList(list(self) + list(other))

    def append(self, command):
        if not isinstance(command,Command):
            command = Command(command)

        super(CommandList,self).append(command)


class Command(object):
    def __init__(self,command_params,out_files= None, tmp_files = None):
        if not isinstance(command_params,list):
            command_params = [command_params]

        command_params = unwrapList(command_params)

        if not out_files:
            out_files = []
        elif not isinstance(out_files,list):
            out_files = [out_files]

        if not tmp_files:
            tmp_files = []
        elif not isinstance(tmp_files,list):
            tmp_files = [tmp_files]

        self.tmp_files = tmp_files

        self.full_command = command_params[0]
        if len(command_params)>1:
            out_files.extend(command_params[1:])

        split_command = str(self.full_command).split(" ")
        self.command = split_command[0]
        if len(split_command)>1:
            self.command_args = " ".join(split_command[1:])
        else:
            self.command_args = ""

        self.out_files = out_files

        self.result = None
        self.err = None

        self.start = None
        self.end = None

    def __str__(self):
        return "{0} -> [{1}]".format(self.full_command,",".join(self.out_files))


    def run(self, verbose = True, silent = False):
        self.start = getTimestamp()
        if verbose:
            printCommand("\n{0}:\t{1}".format(str(self.start), str(self.full_command)))

        if silent:
            os.system("{0} 1>/dev/null".format(str(self.full_command)))
        else:
            os.system("{0}".format(str(self.full_command)))

        self.end = getTimestamp()

    def simulate(self):
        self.start = getTimestamp()
        printExtra("\n{0}:\t{1}".format(str(self.start), str(self.full_command)))

    def run_with_result(self,verbose = True,silent = False):
        self.start = getTimestamp()

        if verbose:
            printCommand("\n{0}:\t{1}".format(str(self.start),str(self.full_command)))

        # P = subprocess.Popen([self.command, self.command_args])
        P = subprocess.Popen([self.command, self.command_args],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.end = getTimestamp()

        output, error = P.communicate()
        if not silent:
            print(output)

        if error:
            if sys.version_info > (3, 0):
                error = error.decode("utf-8")
            printError(error)
            self.err = error
            return

        else:
            if sys.version_info > (3,0):
                output=output.decode("utf-8")
            self.result = output
            CommandHistory.executed.append(self)

            return output


class CommandHistory():
    simulated = CommandList()
    executed = CommandList()
    tmp_files = []

    def get_tmp_files(self):
        file_list = CommandHistory.tmp_files[:]
        for e in CommandHistory.executed:
            if isinstance(e, Command):
                file_list.extend(e.tmp_files)

        return file_list

    def get_out_files(self):
        file_list = []
        for e in CommandHistory.executed:
            if isinstance(e, Command):
                file_list.extend(e.out_files)

        return file_list


class CommandRunner(object):
    runSwitch = True
    permanentTime = 0
    overwrite = False
    silent = False

    _real_run_switch = True

    nii_gz = False
    remove_gz = False

    def __init__(self):
        self.Commands = CommandList()

    @staticmethod
    def flip_run_switch(sim = True):
        """
        Easy to use method for safe flipping the runSwitch. Use this method to temporarily switch on/off the runSwitch.
        :return:
        """
        if sim:
            # CommandRunner._real_run_switch= CommandRunner.runSwitch
            CommandRunner.runSwitch = False
        else:
            CommandRunner.runSwitch = CommandRunner._real_run_switch

    @staticmethod
    def set_run_switch(sim= False):
        """
        Easy to use method for safe defining the runSwitch. Use this method to switch on/off the runSwitch.
        :return:
        """
        CommandRunner._real_run_switch=not(sim)
        CommandRunner.runSwitch = not(sim)


    @classmethod
    def _gz_remover(cls,*file_paths):
        for _f in file_paths:
            if str(_f).endswith(".gz"):
                f = _f
            else:
                f = str(_f)+".gz"
            if os.path.exists(f):
                if cls.runSwitch:
                    printInfo("Existing .gz file '{0}' detected and removed to ensure file consistency.".format(f))
                    os.remove(f)
                else:
                    printWarning("Existing .gz file '{0}' detected".format(f))


    def run(self, store_results = False, verbose=True, autoClear=True, silent = None):
        """
        Run every command in self.Commands, in a serialized way.
        :param verbose: print out command
        :param autoClear: If true, commands are removed after execution.
        :param silence: send command output to /dev/null
        :param overWrite: allow to run the command despite at least one of the output file already exists
        :return:
        """
        if silent is None:
            silent = self.silent

        if not self.runSwitch:
            self.simulate(autoClear)
            return

        for command in self.Commands:
            if self.overwrite==False:
                if any([ageH(os.path.getmtime(str(o)))>self.permanentTime for o in command.out_files if os.path.exists(str(o))]):
                    printWarning("{0}\tThe following command is skipped due to some of the output file are already exists:\n{1}".format(getTimestamp(),command.full_command))
                    continue

            try:
                if self.remove_gz:
                    self._gz_remover(*command.out_files)

                if store_results:
                    command.run_with_result(verbose=verbose,silent=silent)
                else:
                    command.run(verbose=verbose,silent=silent)


            except KeyboardInterrupt:
                if len(command.out_files)>0:
                    printWarning("Progress interrupted!")
                    printInfo("Searching for damaged files...")
                    for o in command.out_files:
                        if os.path.exists(o) and os.path.getsize(o) == 0:
                            printWarning("Damaged file {0} found!".format(o))
                            os.remove(o)
                printError("Program stopped!")
                sys.exit()

        results = []
        if store_results:
            for command in self.Commands:
                # c_res = str(command.result).split("\n")
                # results.append([c_res])
                results.append(command.result)

        if autoClear:
            self.Commands = CommandList()

        return results

    def simulate(self,autoClear=True):
        for command in self.Commands:
            command.simulate()

        if autoClear:
            self.Commands=CommandList()

    def __add__(self, other):
        if isinstance(other,CommandRunner):
            self.Commands.extend(other.Commands)

        if isinstance(other,Command):
            self.Commands.append(other)

        if isinstance(other,str):
            self.Commands.append(Command(other))

        if isinstance(other,list):
            self.Commands.append(Command(other))

        return self

    def append(self,other):
        self.__add__(other)


