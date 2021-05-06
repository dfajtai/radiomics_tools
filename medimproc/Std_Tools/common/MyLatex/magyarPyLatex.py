#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylatex import NoEscape
import unicodedata


magyarLDF="/home/fajtai/py/Common/MyLatex/magyar"

HUN_char_dict = {
    "á": "{\\'a}", "Á": "{\\'A}",
    "é": "{\\'e}", "É": "{\\'E}",
    "í": "{\\'i}", "Í": "{\\'I}",
    "ó": "{\\'o}", "Ó": "{\\'O}",
    "ö": '{\\"o}', "Ö": '{\\"O}',
    "ő": "{\\H{o}}", "Ő": "{\\H{O}}",
    'õ': "{\\H{o}}", "Õ": "{\\H{O}}",
    "ú": "{\\'u}", "Ú": "{\\'U}",
    "ü": '{\\"u}', "Ü": '{\\"U}',
    "ű": '{\\H{u}}', "Ű": '{\\H{U}}',
    "û": '{\\H{u}}', "Û": '{\\H{U}}'}


HUN2ASCII_char_dict = {
    "á": "a", "Á": "A",
    "é": "e", "É": "E",
    "í": "i", "Í": "I",
    "ó": "o", "Ó": "O",
    "ö": 'o', "Ö": 'O',
    "ő": "o", "Ő": "O",
    'õ': "o", "Õ": "O",
    "ú": "u", "Ú": "U",
    "ü": 'u', "Ü": 'U',
    "ű": 'u', "Ű": 'U',
    "û": 'u', "Û": 'U'}


def hun(orig):
    puffer = orig
    for k in HUN_char_dict.keys():
        puffer=puffer.replace(k,HUN_char_dict[k])
    return puffer

def printHUN(string):
    string=hun(string)
    return NoEscape(string)

def hun2eng(orig):
    puffer = orig
    for k in HUN2ASCII_char_dict.keys():
        puffer = puffer.replace(k, HUN2ASCII_char_dict[k])
    return puffer

def uni2hun(orig):
    outstr = orig.encode("utf-8")
    # for k in Unicode2HUN.keys():
    #     outstr=outstr.replace(k,Unicode2HUN[k])
    # print outstr
    # print repr(outstr)
    return outstr
