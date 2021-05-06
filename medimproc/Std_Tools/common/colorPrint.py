#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

pd.set_option('display.width',200)

def star(func):
    def inner(*args, **kwargs):
        print("*" * 30)
        func(*args, **kwargs)
        print("*" * 30)
    return inner

class bcolors:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    #forecolor

    Default = '\033[49m'
    White = '\033[97m'

    LightYellow = '\033[93m'
    Red = '\033[31m'
    Green = '\033[32m'
    LightGreen = '\033[92m'
    Orange = '\033[33m'
    Blue = '\033[34m'
    Purple = '\033[35m'
    LightBlue = '\033[94m'
    LightGray = '\033[37m'


def printCaption(text):
    print("{0}{1}{2}".format(bcolors.White+bcolors.UNDERLINE+bcolors.BOLD,text,bcolors.ENDC))

def strCaption(text):
    return "{0}{1}{2}".format(bcolors.White+bcolors.UNDERLINE+bcolors.BOLD,text,bcolors.ENDC)

def strWhite(text):
    return "{0}{1}{2}".format(bcolors.White,text,bcolors.ENDC)

def printExtra(text):
    print("{0}{1}{2}".format(bcolors.Green,text,bcolors.ENDC))

def printWarning(text):
    print("{0}{1}{2}".format(bcolors.LightYellow,text,bcolors.ENDC))
    # raise

def strYellow(text):
    return "{0}{1}{2}".format(bcolors.LightYellow,text,bcolors.ENDC)

def printError(text):
    print("{0}{1}{2}".format(bcolors.Red + bcolors.BOLD, text, bcolors.ENDC))

def strRed(text):
    return "{0}{1}{2}".format(bcolors.Red, text, bcolors.ENDC)

def printHint(text):
    print("{0}{1}{2}".format(bcolors.LightGray,text,bcolors.ENDC))

def printInfo(text):
    print("{0}{1}{2}".format(bcolors.LightBlue,text,bcolors.ENDC))

def strInfo(text):
    return "{0}{1}{2}".format(bcolors.LightBlue,text,bcolors.ENDC)

def printCommand(text):
    print("{0}{1}{2}".format(bcolors.White,text,bcolors.ENDC))

def printBold(text):
    print("{0}{1}{2}".format(bcolors.White+bcolors.BOLD,text,bcolors.ENDC))

def printEmphInTetx(text,emph):
    str = bcolors.Default
    textList=text.split("*")
    for t in textList[0:-1]:
        str+=t+bcolors.White+bcolors.BOLD+emph+bcolors.Default
    str+=textList[-1]+bcolors.ENDC
    print(str)

def boldText(tetx):
    return bcolors.BOLD+tetx+bcolors.Default

def printDone(pre="",after="",done_text = True):
    doneText = "\n"+bcolors.BOLD
    if pre !="":
        doneText += str(pre)

    if done_text:
        doneText += " Done"

    if after !="":
        doneText+=": {0}".format(str(after))

    doneText+= "\n{0}".format("*"*60)
    print(doneText+bcolors.ENDC+"\n")



