from datetime import datetime
import time

import re

def extract_date(date_str):
    pattern = re.compile("[0-9]{8}")
    match = re.findall(pattern, date_str)
    if len(match) == 1:
        return match[0]
    return ""

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def age(T0):
    if isinstance(T0,float):
        T0 = datetime.fromtimestamp(T0)
    n = datetime.now()
    dT = n -T0
    return dT

def ageH(T0):
    dT = age(T0)
    return dT.days*24.0+dT.seconds/3600.0

def getTimestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getDateDict(T):
    if isinstance(T,float): #timestamp
        T = datetime.fromtimestamp(T)
    strTime = T.strftime("%Y*%m*%d*%H*%M*%S").split("*")
    timeLabels = ["y","m","d","H","M","S"]
    dictPuffer = [(l,int(t)) for t, l in zip(strTime,timeLabels)]
    return dict(dictPuffer)

def getCompactDayDate(T):
    """
    :param T: time in float from os.path.getmtime(file)
    :return: time formatted to YYYYmmmDD, mmm = Jan, Feb, etc.
    """
    dateDict = getDateDict(T)
    monthLabels = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    return str(dateDict["y"])+monthLabels[dateDict["m"]]+str(dateDict["d"]).zfill(2)



def dotted_date_2_plain(dottedDate):
    if isinstance(dottedDate,str):
        return dottedDate.replace(".","")
    else:
        return None

def plain_date_2_dotted(plainDate):
    d = str(plainDate)
    return "{0}.{1}.{2}".format(d[0:4],d[4:6],d[6:8])
