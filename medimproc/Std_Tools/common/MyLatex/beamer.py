#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
from pylatex import Document, Section, Subsection, Table, Math, TikZ, Axis, Plot, Figure, Package, Command, NoEscape, Tabu, MultiColumn, MultiRow
from pylatex.base_classes.command import Arguments

class Frame():

    def __init__(self,*args):
        self.commands = []
        self.args=args[:]

    def append(self,command):
        self.commands.append(command)

    def getFrame(self):
        commands =[]
        framebegin = "\\begin{frame}"
        for a in self.args:
            framebegin+="{"+str(a)+"}"

        commands.append(NoEscape(framebegin))
        commands.extend(self.commands)
        commands.append(Command("end","frame"))
        return commands