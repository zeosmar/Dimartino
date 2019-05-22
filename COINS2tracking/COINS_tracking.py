#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 16:38:48 2019

@author: jcloud
"""

import os, sys
import pandas as pd
import numpy as np
import json
import argparse

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' %message)
        self.print_help()
        sys.exit(2)
        
def gracefulExit():
    parser.print_help()
    exit(2)
    
basePath=os.getcwd()

parser=MyParser(prog='COINS_tracking')
parser.add_argument('-rs','--runsheet',dest='runsheet',required=True)
parser.add_argument('-idir','--source_dir',dest='input_dir',required=True)
parser.add_argument('-tj','--temp_json',dest='temp_json', required=True)
parser.add_argument('--subject_list', dest='subject_list', required=True)

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args=parser.parse_args()

if args.runsheet:
    headr, tailr=os.path.split(args.runsheet)
    if headr=='':
        headr=basePath
        
    fullpathr = os.path.join(headr,tailr)
    runsheet = pd.read_csv(fullpathr)

if args.subject_list:
    f = open(args.subject_list)
    subject_list = f.read().splitlines()
    f.close()

if args.input_dir:
    input_dir = args.input_dir
    
if args.temp_json:
    headj, tailj = os.path.split(args.temp_json)
    if headj == '':
        headj=basePath
    fullpathj = os.path.join(headj, tailj)
    json_path = fullpathj
else:
    json_path = os.path.join(input_dir, 'tracking-template.json')

if not os.path.exists(os.path.join(input_dir,'tracking_templates')):
    os.mkdir(os.path.join(input_dir,'tracking_templates'))
    
with open(json_path) as json_file:
    json_file=json.load(json_file)
    print(json_file)
    
for index, row in runsheet.iterrows():
    with open(json_path) as json_file:
        json_file=json.load(json_file)
        
    for i in list(runsheet.columns):
        subid = row['Scan_Subject_ID']
        if i[-1].isdigit() and 'sub-' + subid in subject_list:
            if row[i] != '0':
                json_file[i] = os.path.join(input_dir, 'sub-' +subid, 'originals', '01+eyeTracker', row[i]+'.edf')
            else:
                json_file[i] = ''
    if 'sub-' + subid in subject_list:     
        with open(os.path.join(input_dir,"tracking_templates/sub-"+str(subid)+"_tracking-template.json"),"w") as fp:
            json.dump(json_file,fp)
