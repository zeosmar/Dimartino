#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 11:02:54 2018

@author: sray
"""

import pandas as pd
import json
import os, sys
from optparse import OptionParser
import argparse

#Take input form user
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' %message)
        self.print_help()
        sys.exit(2)
        
def gracefulExit():
    parser.print_help()
    exit(2)

basePath=os.getcwd()

parser=MyParser(prog="coins2bids")
parser.add_argument("--COINS_BIDS",dest="COINS_BIDS")
parser.add_argument("--temp_json",dest="temp_json")
parser.add_argument("--input_path",dest="input_path")

#Checking if attempt has been made to pass arguments
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args=parser.parse_args()

#import COINS run sheet and COINS run sheet key
if args.COINS_BIDS:
    headr, tailr=os.path.split(args.COINS_BIDS)
    if headr=='':
        headr=basePath
    fullpathr=os.path.join(headr,tailr)
    fnamer,extr=os.path.splitext(tailr)
    COINS_BIDS=pd.read_csv(fullpathr)
else:
    COINS_BIDS=pd.read_csv("/home/sray/Desktop/Desktop/check2/COINS_BIDS.csv")
    
COINS_dcm2bids=COINS_BIDS

if args.temp_json:
    headk, tailk=os.path.split(args.temp_json)
    if headk=='':
        headk=basePath
    fullpathk=os.path.join(headk,tailk)
    fnamek,extk=os.path.splitext(tailk)
    temp_json=fullpathk
else:
    temp_json='/home/sray/Desktop/config_new2.json'
    
if args.input_path:
    heado, tailo=os.path.split(args.input_path)
    if heado=='':
        heado=basePath
    fullpatho=os.path.join(heado,tailo)
    fnameo,exto=os.path.splitext(tailo)
    input_path=fullpatho
else:
    input_path="/projects/zyang/Adri/MB8_MB6_archive/reorganized/sourceData"    

with open(temp_json) as json_file:
    json_data=json.load(json_file)
    print(json_data)
    
with open(temp_json,'r') as f:
        lines=f.readlines()

for j in range(len(COINS_dcm2bids)):
    with open(temp_json,'r') as f:
        lines=f.readlines()
    for i in range(len(json_data["descriptions"])):    
            if str(COINS_BIDS.iloc[j,2]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,2])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,3]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,3])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,4]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,4])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,5]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,5])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,6]).upper().find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,6]).upper()
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,7]).upper().find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,7]).upper()
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,8]).upper().find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,8]).upper()
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,9]).upper().find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,9]).upper()
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,10]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,10])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,11]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,11])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,12]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,12])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            elif str(COINS_BIDS.iloc[j,13]).find(str(json_data["descriptions"][i]["criteria"]["SeriesDescription"])) != -1:
                x=str(COINS_BIDS.iloc[j,13])
                x=x.replace("+"+str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]),"")
                x=x.strip("0_")
                json_data["descriptions"][i]["criteria"]["SeriesNumber"]=unicode(x)
            
    
    for lsize in range(len(lines)):
        if (lines[lsize]=='                "SeriesDescription": "ABCD_T1w_MPR",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "ABCD_T1w_MPR"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "ABCD_T2w_SPC",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "ABCD_T2w_SPC"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "DIFF_137_AP",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "DIFF_137_AP"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "DIFF_137_PA",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "DIFF_137_PA"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "REST1",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "REST1"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "REST2",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "REST2"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "FACES1",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "FACES1"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "FACES2",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "FACES2"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "FMRI_DISTORTION_AP",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "FMRI_DISTORTION_AP"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "FMRI_DISTORTION_PA",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "FMRI_DISTORTION_PA"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))
        elif (lines[lsize]=='                "SeriesDescription": "SpinEcho_Distortion_PA",\n'):
            for i in range(len(json_data["descriptions"])):
                if (str(json_data["descriptions"][i]["criteria"]["SeriesDescription"]) == "SpinEcho_Distortion_PA"):
                    lines[lsize+1]=lines[lsize+1].replace("SNum",str(json_data["descriptions"][i]["criteria"]["SeriesNumber"]))   
    
    if str(COINS_dcm2bids.iloc[j,12])=='0':
        del lines[90:99]
    if str(COINS_dcm2bids.iloc[j,11])=='0':
        del lines[81:90]
    if str(COINS_dcm2bids.iloc[j,5])=='0':
        del lines[72:81]
    if str(COINS_dcm2bids.iloc[j,4])=='0':
        del lines[63:72]
    if str(COINS_dcm2bids.iloc[j,8])=='0':
        del lines[54:63]
    if str(COINS_dcm2bids.iloc[j,7])=='0':
        del lines[45:54]
    if str(COINS_dcm2bids.iloc[j,9])=='0':
        del lines[36:45]
    if str(COINS_dcm2bids.iloc[j,6])=='0':
        del lines[27:36]
    if str(COINS_dcm2bids.iloc[j,13])=='0':
        del lines[18:27]
    if str(COINS_dcm2bids.iloc[j,10])=='0':
        del lines[10:18]
    if str(COINS_dcm2bids.iloc[j,3])=='0':
        del lines[2:10]
    
    change=len(lines)-3
    lines[change]="        }"
    f1=open(input_path+"/sub-"+str(COINS_dcm2bids.iloc[j,1])+"/"+str(COINS_dcm2bids.iloc[j,1]+".json"),"w")
    for item in lines:
        f1.write(item)
    f1.close()
        
    
            