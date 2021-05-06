#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Std_Tools.dcm_tools.dcm_download.dicomsrvtools import DicomSRVTools


def test_download():
    downloader = DicomSRVTools()

    # S = {"PatientID":}
    # result = downloader.download_map07(items = S, outpath= "/home/fajtai/test/dcm_download_test/")


def main():

    pass


if __name__ == '__main__':
    main()