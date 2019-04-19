#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 16:20:13 2019

@author: jcloud
"""

import os, sys
import pandas as pd
import numpy as np
import argparse
import json
import datetime

def contains_alpha(x):
    res = False
    for i in x:
        if i.isalpha():
            res = True
            break
    return res

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

parser=MyParser(prog="COINS_BIDS")
parser.add_argument("--runsheet",dest="runsheet", required=True, help='Path to the COINS run sheet')
parser.add_argument("--keysheet",dest="keysheet", required=True, help='Path to the COINS key sheet')
parser.add_argument("--temp_json",dest="temp_json", required=True, help='Path to config.json')
parser.add_argument("--sub_dir",dest="input_path", required=True, help='Path to subject source directory')

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
    df=pd.read_csv(fullpathr)

if args.keysheet:
    headk, tailk=os.path.split(args.keysheet)
    if headk=='':
        headk=basePath
    
    fullpathk=os.path.join(headk,tailk)
    keysheet=pd.read_csv(fullpathk)
    
scan_output_file = os.path.join(args.input_path, 'selected_scans.csv')
physio_output_file = os.path.join(args.input_path, 'selected_physio.csv')
tracker_output_file = os.path.join(args.input_path, 'selected_track.csv')

scan3cols = [c for c in df.columns if 'Scan3' in c and '.1' not in c]
scan2cols = [c for c in df.columns if 'Scan2' in c and '.1' not in c]
scan1cols = [c for c in df.columns if ('Scan2' not in c and 'Scan3' not in c and 'scan' not in c and '.1' not in c)]
remainingcols = [c for c in df.columns if 'Scan' not in c and '.1' not in c]

df1 = df[scan1cols]
df1 = df1.replace('~<condSkipped>~', '?')
df1 = df1.replace(np.nan, '?')
df2 = df[scan2cols]
df2 = df2.replace('~<condSkipped>~', '?')
df2 = df2.replace(np.nan, '?')
df3 = df[scan3cols]
df3 = df3.replace('~<condSkipped>~', '?')
df3 = df3.replace(np.nan, '?')

l2 = len(df2)
l3 = len(df3)

for x in remainingcols:
    df2[x] = ['?'] * l2
    df3[x] = ['?'] * l3
    
cut = df2['Scan_Scan2_Subject_ID'] != '?'
df2 = df2[cut]

cut = df3['Scan_Scan3_Sub_ID'] != '?'
df3 = df3[cut]

headers1 = list(df1.columns)
for x in range(len(headers1)):
    if 'Scan1' in headers1[x]:
        headers1[x] = headers1[x].replace('Scan1_', '')
    if 'Scan_Headcoil' in headers1[x]:
        headers1[x] = 'Scan_Head_Coil'
    if 'Scan_Sub_ID' in headers1[x]:
        headers1[x] = 'Scan_Subject_ID'
    if 'Scan_Samp_Rate' in headers1[x]:
        headers1[x] = 'Scan_Sampling_Rate'
    test = headers1[x].split('_')
    try:
        if test[1] == 'Run' and len(test[2]) == 1:
            test[2] = '0' + test[2]
            test = '_'.join(test)
            headers1[x] = test
        elif test[1] == 'Run' and len(test[2]) == 2 and contains_alpha(test[2]):
            test[2] = '0' + test[2]
            test = '_'.join(test)
            headers1[x] = test
    except IndexError:
        pass
df1.columns = headers1
        
headers2 = list(df2.columns)
for x in range(len(headers2)):
    if 'Scan2' in headers2[x]:
        headers2[x] = headers2[x].replace('Scan2_', '')
    if 'Scan_Headcoil' in headers2[x]:
        headers2[x] = 'Scan_Head_Coil'
    if 'Scan_Sub_ID' in headers2[x]:
        headers2[x] = 'Scan_Subject_ID'
    if 'Scan_Samp_Rate' in headers2[x]:
        headers2[x] = 'Scan_Sampling_Rate'
    test = headers2[x].split('_')
    try:
        if test[1] == 'Run' and len(test[2]) == 1:
            test[2] = '0' + test[2]
            test = '_'.join(test)
            headers2[x] = test
        elif test[1] == 'Run' and len(test[2]) == 2 and contains_alpha(test[2]):
            test[2] = '0' + test[2]
            test = '_'.join(test)
            headers2[x] = test
    except IndexError:
        pass
df2.columns = headers2
        
headers3 = list(df3.columns)
for x in range(len(headers3)):
    if 'Scan3' in headers3[x]:
        headers3[x] = headers3[x].replace('Scan3_', '')
    if 'Run' in headers3[x]:
        headers3[x] = headers3[x][:8] + '_' + headers3[x][8:]
    if 'Scan_Headcoil' in headers3[x]:
        headers3[x] = 'Scan_Head_Coil'
    if 'Scan_Sub_ID' in headers3[x]:
        headers3[x] = 'Scan_Subject_ID'
    if 'Scan_Samp_Rate' in headers3[x]:
        headers3[x] = 'Scan_Sampling_Rate'
    test = headers3[x].split('_')
    try:
        if test[1] == 'Run' and len(test[2]) == 1:
            test[2] = '0' + test[2]
            test = '_'.join(test)
            headers3[x] = test
        elif test[1] == 'Run' and len(test[2]) == 2 and contains_alpha(test[2]):
            test[2] = '0' + test[2]
            test = '_'.join(test)
            headers3[x] = test
    except IndexError:
        pass
    
df3.columns = headers3

for x, row in df2.iterrows():
    for i in remainingcols:
        df2[i][x] = df1[i][x]
        
for x, row in df3.iterrows():
    for i in remainingcols:
        df3[i][x] = df1[i][x]
        
df2 = df2.drop(0, axis=0)
df2 = df2.drop('Scan_2nd_scan', axis=1)
df3 = df3.drop(0, axis=0)
df3 = df3.drop('Scan_3rd_scan', axis=1)
        
df = df1.copy()
df = df.append(df2, sort=True)
df = df.append(df3, sort=True)
df = df.reset_index(drop=True) 

runsheet = df.copy()
#Get the first row for getting the Scan name columsn later        
listRow=runsheet.iloc[0,:]

#Filter the Scan Names and get indices
scan_names_bool=listRow.str.contains("Run")
scan_names_bool=pd.DataFrame(scan_names_bool)
scan_name_indices=np.array([])
for i in range(scan_names_bool.shape[0]):
    if scan_names_bool.iloc[i].any()==True:
        scan_name_indices=np.append(scan_name_indices,int(i))
        
physio_names_bool = listRow.str.contains('Physio Use?')
physio_names_bool = pd.DataFrame(physio_names_bool)
physio_name_indices = np.array([])
for i in range(physio_names_bool.shape[0]):
    if physio_names_bool.iloc[i].any()==True:
        physio_name_indices=np.append(physio_name_indices, int(i-1))
        

#Store useful scans in list
coins_bids= pd.DataFrame()
for sub in range(1,len(runsheet)):
    if runsheet['Scan_Subject_ID'][sub] != '?' and runsheet['Scan_Run_01'][sub] != '?':
        success_list=np.array([])      
        for i in range(len(scan_name_indices)):
            success_list=np.append(success_list,runsheet.iloc[sub,int(scan_name_indices[i])])
        
        sheet_value=np.array([])        
        for i in range(len(success_list)):
            if success_list[i].isdigit():
                if runsheet.iloc[sub, int(scan_name_indices[i])+1]=='1':
                    sheet_value=np.append(sheet_value, scan_name_indices[i])
        
        scan_value=[]
        scan_name=[]
        
        for i in range(len(sheet_value)):         
            scan_value.append(runsheet.iloc[0,int(sheet_value[i])])
            scan_name.append(runsheet.iloc[sub,int(sheet_value[i])])
        
        subdata=[]
        subdata.append(scan_value) 
        subdata.append(scan_name) 
    
        scans_list=[]
        for i in range(len(keysheet)):
            scans_list.append(keysheet.iloc[i,1])
        
        #extracts df from keysheet and makes all values strings
        key_df=pd.DataFrame(keysheet,columns=['Scan Name Key','Unnamed: 1'])            
        key_df["Scan Name Key"]=key_df["Scan Name Key"].apply(str)
        
        #makes information about subject into a data frame, then transposes
        sub_info = pd.DataFrame(subdata)
        sub_info=sub_info.transpose()
        
        #adds keysheet info to sub info
        sub_info=pd.merge(left=key_df,right=sub_info,left_on="Scan Name Key",right_on=1,how='outer')
        for x in range(len(sub_info[0])):
            try:
                sub_info[0][x] = sub_info[0][x].strip('Run ')
            except AttributeError:
                pass 
                
        sub_info = sub_info.dropna()
            
        #rename untitled column to Scan Name, add a plus to front so correctly formatted
        #for file name convention
        sub_info = sub_info.rename(columns={'Unnamed: 1':'Scan'})
        sub_info['File Name'] = sub_info[0] + '+' + sub_info['Scan']
        
        sub_info = sub_info.reset_index(drop=True)
        
        sub_info = sub_info.drop(labels=['Scan Name Key', 0, 1], axis=1)
        sub_info = sub_info.drop_duplicates('Scan', keep='last')
        sub_info = sub_info.transpose()
        sub_info = sub_info.reset_index(drop=True)
        sub_info.columns = sub_info.iloc[0]
        sub_info = sub_info.drop([0], axis=0)
        
        sub_info['queried_ursi'] = runsheet['queried_ursi'][sub]
        sub_info['Scan_Subject_ID'] = runsheet['Scan_Subject_ID'][sub]
        
        coins_bids = coins_bids.append(sub_info, sort=True)
        coins_bids = coins_bids.replace(np.nan, '0')
        coins_bids = coins_bids.reset_index(drop=True)
        
physio_bids = pd.DataFrame()
for sub in range(1,len(runsheet)):
    if runsheet['Scan_Subject_ID'][sub] != '?' and runsheet['Scan_Run_01'][sub] != '?':
        success_list=np.array([])
        for i in range(len(physio_name_indices)):
            success_list = np.append(success_list, runsheet.iloc[sub, int(physio_name_indices[i])])
            
        sheet_value = np.array([])
        for i in range(len(success_list)):
            if success_list[i] != np.nan:
                if runsheet.iloc[sub, int(physio_name_indices[i]) +1]=='1':
                    sheet_value = np.append(sheet_value, physio_name_indices[i])
                    
        scan_value = []
        scan_name = []
        
        for i in range(len(sheet_value)):
            scan_value.append(runsheet.iloc[sub, int(sheet_value[i])][:5].lower())
            scan_name.append(runsheet.iloc[sub, int(sheet_value[i])])
            
        subdata = []
        subdata.append(scan_value)
        subdata.append(scan_name)
        
        scans_list = []
        for i in range(len(keysheet)):
            scans_list.append(keysheet.iloc[i, 1])
            
        sub_info = pd.DataFrame(subdata)
        
        sub_info = sub_info.dropna()
        sub_info = sub_info.transpose()
        sub_info = sub_info.drop_duplicates(0, keep='last')
        sub_info = sub_info.transpose()
        
        sub_info.columns = sub_info.iloc[0]
        sub_info = sub_info.drop([0], axis=0)
        
        sub_info['queried_ursi'] = runsheet['queried_ursi'][sub]
        sub_info['Scan_Subject_ID'] = runsheet['Scan_Subject_ID'][sub]
        
        physio_bids = physio_bids.append(sub_info, sort=True)
        physio_bids = physio_bids.replace(np.nan, '0')
        physio_bids = physio_bids.reset_index(drop=True)
    
physio_bids = physio_bids[['Scan_Subject_ID', 'queried_ursi', 'rest1', 'rest2', 'face1', 'face2']]
coins_track = physio_bids.copy()
coins_track = coins_track.drop(labels=['rest1', 'rest2'], axis=1)

for i in range(coins_track.shape[0]):
    if coins_track['face1'][i] != '0':
        coins_track['face1'][i] = coins_track['Scan_Subject_ID'][i] + '_1'
    if coins_track['face2'][i] != '0':
        coins_track['face2'][i] = coins_track['Scan_Subject_ID'][i] + '_2'

excel=coins_bids.copy()
excel.head()
excel.to_csv(scan_output_file,index=False)

excel = physio_bids.copy()
excel.head()
excel.to_csv(physio_output_file, index=False)

excel = coins_track.copy()
excel.head()
excel.to_csv(tracker_output_file, index=False)

COINS_BIDS=pd.read_csv(scan_output_file)
 
COINS_dcm2bids=COINS_BIDS

if args.temp_json:
    headk, tailk=os.path.split(args.temp_json)
    if headk=='':
        headk=basePath
    fullpathk=os.path.join(headk,tailk)
    fnamek,extk=os.path.splitext(tailk)
    temp_json=fullpathk
    
if args.input_path:
    heado, tailo=os.path.split(args.input_path)
    if heado=='':
        heado=basePath
    fullpatho=os.path.join(heado,tailo)
    fnameo,exto=os.path.splitext(tailo)
    input_path=fullpatho
    
with open(temp_json) as json_file:
    json_data=json.load(json_file)

for i in range(len(COINS_dcm2bids)):
    with open(temp_json, 'r') as f:
        lines = f.readlines()
    final_lines = lines[:]
    for line in lines:
        if 'SeriesDescription' in line:
            scan = line.split('"')
            scan = scan[3]
            runnum = COINS_BIDS[scan][i]
            index = final_lines.index(line)
            index2 = lines.index(line)
            if runnum != '0':
                runnum = runnum.split('+')
                runnum = str(int(runnum[0]))
                final_lines[index+1] = lines[index2+1].replace('SNum', runnum)
            else:
                if 'ABCD' in scan:
                    del final_lines[index-4:index+4]
                else:
                    del final_lines[index-5:index+4]
    final_lines[-3] = final_lines[-3].replace(',', '')  
    try:
        f=open(os.path.join(input_path,"sub-"+str(COINS_dcm2bids['Scan_Subject_ID'][i]),str(COINS_dcm2bids['Scan_Subject_ID'][i])+".json"),"w")
        for item in final_lines:
            f.write(item)
        f.close()
    except IOError:
        f = open(os.path.join(input_path, 'error_log.txt'), 'a')
        f.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'COINS_BIDS_setup', COINS_dcm2bids['Scan_Subject_ID'][i], 'subject not in source folder'))
        f.close()
    
            





