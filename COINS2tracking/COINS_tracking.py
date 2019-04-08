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
parser.add_argument('-idir','--input_dir',dest='input_dir',required=True)
parser.add_argument('-tj','--temp_json',dest='temp_json')

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

runsheet = runsheet.drop_duplicates(subset='SubID: Study:9580')

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
    
listRow = runsheet.iloc[0,:]

if not os.path.exists(os.path.join(input_dir,'tracking_templates')):
    os.mkdir(os.path.join(input_dir,'tracking_templates'))
    
with open(json_path) as json_file:
    json_file=json.load(json_file)
    print(json_file)
    
with open(json_path,'r') as f:
    lines = f.readlines()
    
scan_names_bool = listRow.str.contains('Physio')
scan_names_bool = pd.DataFrame(scan_names_bool)
newList1 = np.array([])
for i in range(scan_names_bool.shape[0]):
    if scan_names_bool.iloc[i].any()==True:
        newList1=np.append(newList1,int(i))
        
newList = np.array([])
for i in range(0,len(newList1),2):
    if (i != len(newList)-2):
        newList=np.append(newList,newList1[i])
        
coins_bids=[]
for sub in range(1, len(runsheet)):
    success_list=np.array([])
    for i in range(len(newList)):
        success_list=np.append(success_list,runsheet.iloc[sub,int(newList[i])])
        
    sheet_value = np.array([])
    for i in range(len(success_list)):
        if 'Face1' in success_list[i]:
            if runsheet.iloc[sub,int(newList[i])+1]=='1':
                sheet_value=np.append(sheet_value,newList[i])
        elif 'Face2' in success_list[i]:
            if runsheet.iloc[sub,int(newList[i])+1]=='1':
                sheet_value=np.append(sheet_value,newList[i])
                
    scan_value = []
    scan_name = []
    
    for i in range(len(sheet_value)):
        scan_value.append(runsheet.iloc[0,int(sheet_value[i])])
        scan_name.append(runsheet.iloc[sub,int(sheet_value[i])])
        
    subdata = []
    subdata.append(scan_value)
    subdata.append(scan_name)

    
    with open(json_path) as json_file:
        json_file=json.load(json_file)
        
    df = pd.DataFrame(np.zeros((1,2)),columns=['Face1','Face2'])
    for j in range(len(subdata[1])):
        if subdata[1][j].find('Face1') != -1:
            df.iloc[0,0]=subdata[1][j]
            f = os.path.join(input_dir,'sub-'+runsheet['Scan_scanID'][sub]+'/originals/01+eyeTrackerData/'+runsheet['Scan_scanID'][sub]+'_'+subdata[1][j][-1]+'.edf')
            if os.path.exists(f):
                json_file['face1']=unicode(f)
        if subdata[1][j].find('Face2') != -1:
            df.iloc[0,1]=subdata[1][j]
            f = os.path.join(input_dir,'sub-'+runsheet['Scan_scanID'][sub]+'/originals/01+eyeTrackerData/'+runsheet['Scan_scanID'][sub]+'_'+subdata[1][j][-1]+'.edf')
            if os.path.exists(f):
                json_file['face2']=unicode(f)
    
    if json_file['face1'] == unicode("face1_path"):
        json_file['face1']=unicode('')
    if json_file['face2'] == unicode("face2_path"):
        json_file['face2']=unicode('')
            
    with open(os.path.join(input_dir,'tracking_templates/sub-'+str(runsheet['Scan_scanID'][sub]) + '_tracking-template.json'), 'w') as fp:
        json.dump(json_file, fp)
