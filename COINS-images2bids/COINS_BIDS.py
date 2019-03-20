#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 09:54:55 2018

@author: shrutiray
"""

import os, sys
import pandas as pd
import numpy as np
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

parser=MyParser(prog="COINS_BIDS")
parser.add_argument("-rs","--runsheet",dest="runsheet")
parser.add_argument("-ks","--keysheet",dest="keysheet")
parser.add_argument("-op","--output",dest="output")


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

if args.keysheet:
    headk, tailk=os.path.split(args.keysheet)
    if headk=='':
        headk=basePath
    
    fullpathk=os.path.join(headk,tailk)
    keysheet=pd.read_csv(fullpathk)
    
if args.output:
    heado, tailo=os.path.split(args.output)
    if heado=='':
        heado=basePath
    
    fullpatho=os.path.join(heado,tailo)
    output_file=fullpatho


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




