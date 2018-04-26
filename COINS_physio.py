#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 16:33:17 2018

@author: sray
"""

import os, sys
import pandas as pd
import numpy as np
import json
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

parser=MyParser(prog="COINS_physio")
parser.add_argument("-rs","--runsheet",dest="runsheet")
parser.add_argument("-id","--input_dir",dest="input_dir")
parser.add_argument("-tj","--temp_json",dest="temp_json")


#Checking if attempt has been made to pass arguments
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args=parser.parse_args()

#import COINS run sheet and COINS run sheet key
if args.runsheet:
    headr, tailr=os.path.split(args.runsheet)
    if headr=='':
        headr=basePath
    
    fullpathr=os.path.join(headr,tailr)
    runsheet=pd.read_csv(fullpathr)
else:
    runsheet=pd.read_csv('/home/sray/Desktop/physio/COINS_run_sheet_output.csv')

if args.input_dir:
    input_dir=args.input_dir

if args.temp_json:
    headj,tailj=os.path.split(args.temp_json)
    if headj=='':
        headj=basePath
    fullpathj=os.path.join(headj,tailj)    
    json_path=fullpathj
    

listRow=runsheet.iloc[0,:]

#json_path="/home/sray/Desktop/physio/physio-template.json"

with open(json_path) as json_file:
    json_file=json.load(json_file)
    print(json_file)
    
with open(json_path,'r') as f:
        lines=f.readlines()

#Filter the Scan Names and get indices
scan_names_bool=listRow.str.contains("Physio")
scan_names_bool=pd.DataFrame(scan_names_bool)
newList1=np.array([])
for i in range(scan_names_bool.shape[0]):
    if scan_names_bool.iloc[i].any()==True:
        newList1=np.append(newList1,int(i))

newList=np.array([])       
for i in range(0,len(newList1),2):
    if (i != len(newList)-2):
        newList=np.append(newList,newList1[i])
    
coins_bids=[]
for sub in range(1,len(runsheet)):
    success_list=np.array([])      
    for i in range(len(newList)):
        success_list=np.append(success_list,runsheet.iloc[sub,int(newList[i])])
    
    sheet_value=np.array([])        
    for i in range(len(success_list)):
        if 'Rest1' in success_list[i]:
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif 'Rest2' in success_list[i]:
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif 'Face1' in success_list[i]:
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif 'Face2' in success_list[i]:
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])   

    scan_value=[]
    scan_name=[]
    
    for i in range(len(sheet_value)):         
        scan_value.append(runsheet.iloc[0,int(sheet_value[i])])
        scan_name.append(runsheet.iloc[sub,int(sheet_value[i])])
    
    subdata=[]
    subdata.append(scan_value) 
    subdata.append(scan_name) 
    
    df = pd.DataFrame(np.zeros((1,4)),columns=["Rest1","Rest2","Face1","Face2"])
    for j in range(4):
        if subdata[1][j].find('Face1')!=-1:
            df.iloc[0,2]=subdata[1][j]
            json_file["face1"]=unicode(input_dir+"sub-"+runsheet["Scan_scanID"][sub]+"/originals/01+physio/sub-"+runsheet["Scan_scanID"][1]+"_"+subdata[1][j].lower()+".acq")
        elif subdata[1][j].find('Face2')!=-1:
            df.iloc[0,3]=subdata[1][j]
            json_file["face2"]=unicode(input_dir+"sub-"+runsheet["Scan_scanID"][sub]+"/originals/01+physio/sub-"+runsheet["Scan_scanID"][1]+"_"+subdata[1][j].lower()+".acq")
        elif subdata[1][j].find('Rest1')!=-1:
            df.iloc[0,0]=subdata[1][j]
            json_file["rest1"]=unicode(input_dir+"sub-"+runsheet["Scan_scanID"][sub]+"/originals/01+physio/sub-"+runsheet["Scan_scanID"][1]+"_"+subdata[1][j].lower()+".acq")
        elif subdata[1][j].find('Rest2')!=-1:
            df.iloc[0,1]=subdata[1][j]
            json_file["rest2"]=unicode(input_dir+"sub-"+runsheet["Scan_scanID"][sub]+"/originals/01+physio/sub-"+runsheet["Scan_scanID"][1]+"_"+subdata[1][j].lower()+".acq")
    
    with open(input_dir+"sub-"+runsheet["Scan_scanID"][sub]+"/originals/01+physio/"+runsheet["Scan_scanID"][sub]+".json","w") as fp:
        json.dump(json_file,fp)
    