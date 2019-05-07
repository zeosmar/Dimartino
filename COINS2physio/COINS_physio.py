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
parser.add_argument("-rs","--runsheet",dest="runsheet",required=True)
parser.add_argument("-idir","--source_dir",dest="input_dir",required=True)
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
    

if args.input_dir:
    input_dir=args.input_dir

if args.temp_json:
    headj,tailj=os.path.split(args.temp_json)
    if headj=='':
        headj=basePath
    fullpathj=os.path.join(headj,tailj)    
    json_path=fullpathj
else:
	json_path=os.path.join(input_dir,"physio-template.json")
    

if not os.path.exists(os.path.join(input_dir,"physio_templates")):
    os.mkdir(os.path.join(input_dir,"physio_templates"))

with open(json_path) as json_file:
    json_file=json.load(json_file)
    print(json_file)

#Filter the Scan Names and get indices
 
for index, row in runsheet.iterrows():
    with open(json_path) as json_file:
        json_file=json.load(json_file)
        
    for i in list(runsheet.columns):
        subid = row['Scan_Subject_ID']
        if i[-1].isdigit():
            if row[i] != '0':
                json_file[i] = os.path.join(input_dir, 'sub-' +subid, 'originals', '01+physio', 'sub-' +subid+ '_' +row[i]+'.acq')
            else:
                json_file[i] = ''

    with open(os.path.join(input_dir,"physio_templates/sub-"+str(subid)+"_physio-template.json"),"w") as fp:
        json.dump(json_file,fp)
    
