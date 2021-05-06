#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import pydicom
import math
import nibabel as nib
import os
import shutil
import sys
import time
from pydicom.dataset import Dataset
from optparse import OptionParser

import numpy as np
import medicalImageTool as mit

import medinfo as mi


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def timestamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")+" :: "#%Y-%m-%d
    return st

def generateStrNumber(num,value):
    snum=str(num)
    l=len(snum)
    for i in range(0,value-l):
        snum="0"+snum
    return snum

#NOS=Number Of Slices
def save_dcm(affine,data,path , NOS=None, offset=[0,0,0]):
    global infiles
    global outfiles
    global dcmfile
    global opts
    global hdr

    print(affine)
    print(nib.aff2axcodes(affine))
    # ly = len(data[0,:,0])
    # lx = len(data[:,0,0])
    # lz = len(data[:, 0, 0])
    # print ly
    step = {}
    step[0] = math.sqrt(np.sum(np.square(affine[:, 0])))
    step[1] = math.sqrt(np.sum(np.square(affine[:, 1])))
    step[2] = math.sqrt(np.sum(np.square(affine[:, 2])))
    start={}
    start[0]=affine[0,3]+offset[0]
    start[1] = affine[1, 3] + offset[1]
    start[2] = affine[1, 3] + offset[2]

    rotM = np.zeros((3, 3))
    rotM[:, 0] = affine[:3, 0] / step[0]
    rotM[:, 1] = affine[:3, 1] / step[1]
    rotM[:, 2] = affine[:3, 2] / step[2]
    print(rotM*np.array([affine[0,3],affine[1,3],affine[2,3]]))
    rotx = math.atan2(rotM[2, 1], rotM[2, 2]) * 180 / math.pi
    roty = math.atan2(-rotM[2, 0], math.sqrt(np.sum([np.square(rotM[2, 1]), np.square(rotM[2, 2])]))) * (180 / math.pi)
    rotz = math.atan2(rotM[0, 1], rotM[0, 0]) * 180 / math.pi
    print('Rotx= ', str(rotx))
    print('Roty= ', str(roty))
    print('Rotz= ', str(rotz))

    #read dicom
    dcm = pydicom.read_file(dcmfile)
    #print dcm

    #------------------- get data & set start values -----------------------------------
    #sliceLocation
    SL=affine[2,3]
    #SliceStep
    ST=step[2] #dcm.SliceThicknes
    SOPIUID = dcm.SOPInstanceUID

    # print SOPIUID
    FSOPIUID = SOPIUID.rsplit(".", 1)[0]
    LSOPIUID = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + SOPIUID.rsplit(".", 1)[1][-5:]
    # print LSOPIUID
    for i in range(5, 16):
        if LSOPIUID[-i] != "0" and LSOPIUID[-i] != "9":
            LLSOPIUID = int(LSOPIUID[-5:])
            LFSOPIUID = LSOPIUID[:-5]
        # print str(UID)
    IPP = np.array([start[0],start[1],start[2]])
    IN = 1

    #-------------------set constant values
    SIUID=dcm.SeriesInstanceUID
    if len(SIUID) == 58:
        NSIUID=SIUID.rsplit(".",4)[0]+"."+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")+SIUID.rsplit(".",4)[1][-5:]+".0.0.0"
    else:
        NSIUID=SIUID.rsplit(".",1)[0]+"."+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")+SIUID.rsplit(".",1)[1][-5:]
    dcm.SeriesInstanceUID=NSIUID
    maxt=np.iinfo(dcm.pixel_array.dtype).max
    maxd=np.max(data)
    slope=maxt/maxd

    ds=dcm

    ds.Modality = dcm.Modality
    ds.StudyInstanceUID = dcm.StudyInstanceUID
    ds.SeriesInstanceUID = dcm.SeriesInstanceUID
    ds.SOPInstanceUID = dcm.SOPInstanceUID
    ds.SOPClassUID = dcm.file_meta.MediaStorageSOPClassUID#'=MRImageStorage'#'WS1_Capture_Image_Storage'
    if opts.atlas:
        ds.SecondaryCaptureDeviceManufctur = 'SPM'
    ## These are the necessary imaging components of the FileDataset object.
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.HighBit = 11
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.PixelSpacing = [step[0], step[1]]
    #ds.SmallestImagePixelValue = '\\x00\\x00'
    #ds.LargestImagePixelValue = '\\xff\\xff'
    ds.RescaleSlope = 1 #/slope
    ds.StudyDescription=dcm.StudyDescription
    if opts.sd:
        ds.SeriesDescription = opts.sd
    else:
        ds.SeriesDescription = dcm.SeriesDescription

    R = mit.RotMX(data, affine)



    vect=R[0:3,0].tolist()+R[0:3,1].tolist()
    print("new:\n",R)
    print("affine:\n",affine)
    print("vect:",vect)
    ds.ImageOrientation=vect
    print(vect)
    ds.ImageOrientationPatient=[1,0,0,0,1,0]

    lz = len(data[0,0,:])

    if NOS==None:
        NOS==lz

    # if not os.path.exists(path):
    #     os.makedirs(path)
    for i in range(0,NOS):
        # ---------------set values-------------------
        if opts.atlas:
            slice=data[:,:,i] #*slope
        else:
            slice = data[::-1, :, i] #* slope
        name = outfiles + generateStrNumber(i, 4)

        #------------------set dicom values----------------
        #ds.ContentDate = str(datetime.date.today()).replace('-', '')
        #ds.ContentTime = str(time.time())  # milliseconds since the epoch

        ds.SOPInstanceUID=FSOPIUID+"."+LFSOPIUID+str(LLSOPIUID)
        #print IPP.tolist()
        ds.ImagePositionPatient = IPP.tolist()
        ds.SliceLocation=IPP[2]
        ds.InstanceNumber=IN
        ds.Columns = slice.shape[0]
        ds.Rows = slice.shape[1]
        ds.RescaleIntercept = -1024

        #print str(slice.dtype)[0]
        # if mind <0 :
        #     slice = slice.astype(np.int16)
        # else:
        #     slice = slice.astype(np.uint16)
        slice = slice.astype(np.uint16)
        ds.PixelData =np.rot90(slice).tostring()
        #dcm.PixelData = np.rot90(slice).tostring()
        #-----------------------save dicom file----------------
        if opts.ext:
            ds.save_as(path+"/"+name+".dcm")
        else:
            ds.save_as(path + "/" + name)

        #--------------------------set next slice values------------------
        #print IPP
        IPP=IPP+R[0:3,2]
        #print IPP.tolist()
        SL=SL+ST
        LLSOPIUID=LLSOPIUID+1
        IN=IN+1


def main():
    global infile
    global outfiles
    global dcmfile
    global opts
    global hdr

    usage = "%prog [options] <in.nii or in.mnc> <sourcedcm> <outdir>"
    parser=OptionParser(usage=usage)
    parser.add_option("-p", "--prefix", dest="prefix", default="scan", type="string",help="Set output prefix.")
    parser.add_option("-s","--si","--study_id",dest="si",default="noname", type="string", help="Set output Patient Name for dicom.")
    parser.add_option("-e","--ext", dest="ext", action="store_true", help="Add .dcm extension.")
    parser.add_option("-a", "--atlas", dest="atlas", action="store_true", help="Use if image is in atlas space.")
    parser.add_option("-d","--sd","--SeriesDescription", dest="sd", type="string", default=None, help="Set Series Description [default=%default].", metavar="sd" )
    parser.add_option("-n","--sn","--SeriesNumber", dest="sn", type="int", default=10000, help="Set Series Description [default=%default].", metavar="sn" )
    (opts,args)=parser.parse_args()

    if len(args)==3:
        infile=args[0]
        dcmfile=args[1]
        outdir=args[2]
        outfiles=opts.prefix
    else:
        parser.print_help()
        sys.exit()

    # print affine
    # print nib.aff2axcodes(affine)
    data, affine = mit.LoadImage(infile)
    # print(affine)
    #
    # tmpdcm="/tmp/dcm"
    # if os.path.exists(tmpdcm):
    #     shutil.rmtree(tmpdcm)
    # tmpmnc="/tmp/mnc/"
    # os.makedirs(tmpdcm)
    # save_dcm(affine, data, tmpdcm, 2)
    # cmd='/home/csoka/bin/convert.py -d dcm -m mnc /tmp | grep Created:'
    # # os.system(cmd)
    # tmp=os.popen(cmd)
    # out=tmp.read().split("Created:  ")[1]
    # #out=out.replace('_','\_')
    # out=out.strip()
    # print(out)
    # miinfo=mi.info(out)
    # start=miinfo.get_start()
    # # print("start:",start)
    # # print("affine:",affine[0:3,3])
    # offset=start-affine[0:3,3]
    # offset[2]=-offset[2]
    # print(offset)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    save_dcm(affine, data, outdir, len(data[0,0,:]))

    cmd=""
    #shutil.rmtree(tmpdcm)

    print(timestamp(),"Ended: ",bcolors.OKBLUE,sys.argv[0].split("/")[-1],bcolors.ENDC)
    sys.stdout.flush()
    sys.modules[__name__].__dict__.clear()


if (__name__=="__main__"):
    main()
