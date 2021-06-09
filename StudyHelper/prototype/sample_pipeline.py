#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os,sys

NoneType = type(None)

import numpy as np

from Std_Tools.img_proc.IO import read_image, NibImg
from Std_Tools import extendable_file as ex

from Std_Tools._template_paths_ import *

from Std_Tools.common.command_runner.command_runner import CommandRunner, temp_sim, temp_run
from Std_Tools.common.py_io import py_copy, py_remove, py_mkdirs, py_link
from Std_Tools.StudyHelper import *


class epi_alff_subject(Subject):
    def __init__(self, sid, n, **kwargs):
        super(epi_alff_subject, self).__init__(sid=sid, n=n, **kwargs)

    def alff_pipeline(self):
        preprocessed_fmri_path = self.mods.rfmri_w.get_imgs_with_pre("awrmc")


class epi_alff_pipeline(base_cli):
    _study_name = "epi-test"

    template = T1_brain_2mm

    def __init__(self, *args, **kwargs):
        super(epi_alff_pipeline, self).__init__(*args, **kwargs)
        Study.initWithDB(epi_alff_pipeline._study_name)

        epi_alff_subject_kwargs = {}

        self.Subjects = StudySubjects.get_subjects(epi_alff_pipeline._study_name, T=epi_alff_subject, **epi_alff_subject_kwargs)

    @staticmethod
    def readInput():
        usage = "%prog -sid sid1,[sid2,...] [options]\n" \
                "\nRun epi_alff_pipeline for given subjects."

        parser = ModifiedOptionParser(usage=usage)
        parser = base_cli.append_parser(parser)
        # pipeline_options = OptionGroup(parser, "Pipeline options",
        #                                "In this section you can set pipeline specific options")
        # pipeline_options.add_option("--simants", dest="simants", help="Include this if you want to simulate ANTs",
        #                             default=False, action="store_true")

        # parser.add_option_group(pipeline_options)

        CLI_init = base_cli.read_input(parser=parser, T=epi_alff_pipeline, study_name=epi_alff_pipeline._study_name)

        return CLI_init


    def main_pipeline(self):
        CommandRunner.overwrite = self.overwrite

        IDs = self.id_collect()
        IDs.sort()

        for id in IDs:
            measurements = self.Subjects[id]
            for S in measurements:
                if isinstance(S, epi_alff_subject):
                    if not S.n in self.n_s:
                        continue

                    S.alff_pipeline()

def main():
    study = epi_alff_pipeline.readInput()
    study.main_pipeline()


if __name__ == "__main__":
    main()