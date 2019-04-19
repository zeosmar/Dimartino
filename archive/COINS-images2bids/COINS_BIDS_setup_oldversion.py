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
    
output_file = os.path.join(args.input_path, 'selected_scans.csv')

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
            print(test)
            headers1[x] = test
        elif test[1] == 'Run' and len(test[2]) == 2 and contains_alpha(test[2]):
            test[2] = '0' + test[2]
            test = '_'.join(test)
            print(test)
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
            print(test)
            headers2[x] = test
        elif test[1] == 'Run' and len(test[2]) == 2 and contains_alpha(test[2]):
            test[2] = '0' + test[2]
            test = '_'.join(test)
            print(test)
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
            print(test)
            headers3[x] = test
        elif test[1] == 'Run' and len(test[2]) == 2 and contains_alpha(test[2]):
            test[2] = '0' + test[2]
            test = '_'.join(test)
            print(test)
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
scan_names_bool=listRow.str.contains("Scan Name")
scan_names_bool=pd.DataFrame(scan_names_bool)
newList=np.array([])
for i in range(scan_names_bool.shape[0]):
    if scan_names_bool.iloc[i].any()==True:
        newList=np.append(newList,int(i))
        

#Store useful scans in list
coins_bids=[]
for sub in range(1,len(runsheet)):
    success_list=np.array([])      
    for i in range(len(newList)):
        success_list=np.append(success_list,runsheet.iloc[sub,int(newList[i])])
    
    sheet_value=np.array([])        
    for i in range(len(success_list)):
        if success_list[i]=='1':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='2':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='3':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='4':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='5':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='6':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='7':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='8':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='9':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='10':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='11':
            if runsheet.iloc[sub,int(newList[i])+1]=="1":
                sheet_value=np.append(sheet_value,newList[i])
        elif success_list[i]=='12':
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

    scans_list=[]
    for i in range(len(keysheet)):
        scans_list.append(keysheet.iloc[i,1])
    
    df1=pd.DataFrame(keysheet,columns=['Scan Name Key','Unnamed: 1'])            
    df1["Scan Name Key"]=df1["Scan Name Key"].apply(str)
    df = pd.DataFrame(subdata)
    df2=df.transpose()
    df3=pd.merge(left=df1,right=df2,left_on="Scan Name Key",right_on=1,how='outer')
    try:
        df3[0]=df3[0].str[:-10].astype(str)
    except:
        df3[0]=df3[0][:-10].astype(str)
    df3["Scan Name"]=0
    df3["Scan Name"]=df3[0]+"+"+df3["Unnamed: 1"]
    df3=df3.dropna()
    df3=df3.reset_index()
    df4=pd.DataFrame(df3, columns=["Scan Name"])
    df4=df4.transpose()
    df4.reset_index(drop=True,inplace=True)
    df4.insert(loc=0,column='Queried_ursi',value=runsheet["queried_ursi"][sub])
    df4.insert(loc=1,column='Scan_scanID',value=runsheet["Scan_scanID"][sub])
    df5=pd.DataFrame(scans_list,columns=["scans_list"])
    df5["subj_scan"]=0
    coins=[]
    coins.append(runsheet["queried_ursi"][sub])
    coins.append(runsheet["Scan_scanID"][sub])
    
   
    for i in range(len(df5)):
        for j in range(len(df3)):
            if (df5.iloc[i,0]==df3.iloc[j,2]):
                df5.iloc[i,1]=df3.iloc[j,5]
            else:
                continue
        
    
    for i in range(len(df5)):
        coins.append(df5["subj_scan"][i])
    coins_bids.append(coins)

excel=pd.DataFrame(coins_bids,columns=["URSI","subID","AAHead_scout","ABCD_T1w_MPR","FMRI_DISTORTION_AP","FMRI_DISTORTION_PA","REST1","FACES1","FACES2","REST2","ABCD_T2w_SPC","SpinEcho_Distortion_AP","SpinEcho_Distortion_PA","DIFF_137_AP"])
excel.head()
excel.to_csv(output_file,index=False)

COINS_BIDS=pd.read_csv(output_file)
 
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

    if COINS_dcm2bids.iloc[j, 1] == '80103':
        break
    try:
        f1=open(os.path.join(input_path,"sub-"+str(COINS_dcm2bids.iloc[j,1]),str(COINS_dcm2bids.iloc[j,1])+".json"),"w")
        for item in lines:
            f1.write(item)
        f1.close()
    except IOError:
        print('{} not found in source directory'.format(COINS_dcm2bids.iloc[j,1]))
        
    
            





