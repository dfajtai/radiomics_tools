#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, datetime
import os,sys
import command_logger
from optparse import OptionParser


sys.path.insert(0, '/home/fajtai/py/')
from Common.colorPrint import *
from Common.MyTime import *
from Common.MyList import *

# os.umask(002)

class MyLog(object):
    '''
    Simple interface for log proposes
    '''

    def __init__(self, logName="", logDir="", logSwitch = True):
        self._logDir = logDir
        self._logName = logName
        self._logSwitch = logSwitch

    @property
    def logDir(self):
        return self._logDir

    @logDir.setter
    def logDir(self,logDir):
        self._logDir = logDir

    @property
    def logSwitch(self):
        return self._logSwitch

    @logSwitch.setter
    def logSwitch(self,logSwitch):
        if type(logSwitch) != bool:
            raise TypeError
        self._logSwitch = logSwitch

    @property
    def logName(self):
        return self._logName

    @logName.setter
    def logName(self, logName):
        self._logName = logName

    def _defLogger(self):
        self.logger = command_logger.getLogger(self._logName)
        hdlr = command_logger.FileHandler(os.path.join(self._logDir, self._logName + "-log.log"))
        formatter = command_logger.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(command_logger.DEBUG)