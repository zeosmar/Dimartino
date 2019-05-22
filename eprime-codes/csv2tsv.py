#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 22:10:22 2017

@author: sray
"""

import sys
import os
import pandas as pd
import argparse
import datetime

class MyParser(argparse.ArgumentParser):
    def error(self,message):
        sys.stderr.write('error: %s \n' % message)
        self.print_help()
        sys.exit(2)

#number of trials per prompt including the prompt
ntplusp=7 

#accept input at the command window and store the data if argument passed
parser = MyParser(prog="Convert eprime .csv to .tsv")
parser.add_argument("--source_dir", dest = "input_dir", required = True, help='Directory with subject dicoms')
parser.add_argument("--bids_dir", dest = "output_dir", required=True, help='Directory with bids organized data')
parser.add_argument("--subject_list", dest = "runsheet", required=True, help='List of subjects')
args=parser.parse_args()

if args.input_dir:
    csvpath=args.input_dir
    sys.path.append(csvpath)
if args.output_dir:
    newpath=args.output_dir
if args.runsheet:
    runsheet = args.runsheet
       
path=os.getcwd()

#create list of number of csv files per subID and write a log file if nmber of runs less than or greater than 2
def extension_tsv(csvpath,f,newpath):

    cmd2="ls " + csvpath +"/"+f+"/eprime_csvfiles/*.csv > " + csvpath +"/"+f+"/eprime_csvfiles/csv_list.txt"
    os.system(cmd2)
    csv_list=open(csvpath+"/"+f+"/eprime_csvfiles/csv_list.txt",'r')
    runs_eprime=sum(1 for line in csv_list)

    if runs_eprime < 2 or runs_eprime > 2:
        if not os.path.isfile(csvpath + "/" + f + "/runtime_log.txt"):
            os.mknod(csvpath + "/" + f + "/runtime_log.txt")
        runtime_log=open(csvpath + "/" + f + "/runtime_log.txt","a")
        runtime_log.write("Number of runs for subject - "+ f + " : " + str(runs_eprime) +"\n")
    return csv_list

#Returns dataframe with columns required      
def csv_df(f2):
    f2=f2.strip("\n")

    df = pd.read_csv(f2, usecols=['SyncSlide.OnsetTime','Procedure','ExperimenterWindow.OnsetTime','StimSlide.OnsetToOnsetTime','StimSlide.OnsetTime','StimSlide.RESP','StimSlide.ACC','StimSlide.CRESP','StimSlide.RT'])     
    csv1=f2.strip(".csv")
    head,tail=os.path.split(csv1)
    ref_p=df.loc[0,"SyncSlide.OnsetTime"]/1000
    b=ref_p
    df['ReferencePoint']=b
    df["Onset"]=0
      
    #convert to seconds
    for i in range(len(df)):
        if (pd.isnull(df["StimSlide.OnsetTime"].loc[i])):
            df.loc[i,"StimSlide.OnsetTime"]=df.loc[i,"StimSlide.OnsetTime"]
        else:
            df.loc[i,"StimSlide.OnsetTime"]=df.loc[i,"StimSlide.OnsetTime"]/1000
            df.loc[i,"Onset"]=df.loc[i,"StimSlide.OnsetTime"]-df.loc[i,"ReferencePoint"]
     
    #delete rows not required
    df=df[df.Procedure != "InitialTR"]  
    df=df[df.Procedure != "TwoSecFixPROC"]  
    df=df.reset_index(drop=True)    
    
    #reindexing and changing labels        
    new_index=(0,len(df))
    df.reindex(new_index)
    for i in range(0,len(df),ntplusp):
        if(df.loc[i,"Procedure"] =="ShapePromptPROC"):
            for j in range(1,ntplusp):
                a=i+j
                df.loc[a,"Procedure"]="Shape" 
        elif(df.loc[i,"Procedure"] =="FacePromptPROC"):
            for j in range(1,ntplusp):
                a=i+j
                df.loc[a,"Procedure"]="Face"
        else:
            df.loc[i,"Procedure"]=df.loc[i,"Procedure"]
    
    df=df[df.Procedure != "ShapePromptPROC"]
    df=df[df.Procedure != "FacePromptPROC"]
    df["StimSlide.OnsetToOnsetTime"]=df["StimSlide.OnsetToOnsetTime"]/1000
    df["Duration"]=df["StimSlide.OnsetToOnsetTime"]
    df["StimSlide.RT"]=df["StimSlide.RT"]/1000
    
    #convert null to "n/a" for BIDS compatibility
    df.loc[df["StimSlide.OnsetTime"].isnull(),"StimSlide.OnsetTime"]="n/a"
    df.loc[df["ExperimenterWindow.OnsetTime"].isnull(),"ExperimenterWindow.OnsetTime"]="n/a"
    df.loc[df['StimSlide.OnsetToOnsetTime'].isnull(),'StimSlide.OnsetToOnsetTime']="n/a"
    df.loc[df["Procedure"].isnull(),"Procedure"]="n/a"
    df.loc[df["StimSlide.RESP"].isnull(),"StimSlide.RESP"]="n/a"
    df.loc[df["StimSlide.ACC"].isnull(),"StimSlide.ACC"]="n/a"
    df.loc[df["StimSlide.CRESP"].isnull(),"StimSlide.CRESP"]="n/a"
    df.loc[df["Duration"].isnull(),"Duration"]="n/a"
    df.loc[df["StimSlide.RT"].isnull(),"StimSlide.RT"]="n/a"
    
    #store labels as accepted in BIDS format
    df["onset"]=df["Onset"]
    df["procedure"]=df["Procedure"]
    df["duration"]=df["Duration"]
    df["reaction_time"]=df["StimSlide.RT"]
    df["accuracy"]=df["StimSlide.ACC"]
    df["response"]=df["StimSlide.RESP"]
    df["correct_response"]=df["StimSlide.CRESP"]
                             

    df=df[["onset","duration","procedure","reaction_time","accuracy","response","correct_response"]]


    df=df.reset_index(drop=True)
    
    for i in range(0,len(df)):
        if (df.loc[i,"response"]== "n/a"):
            df.loc[i,"accuracy"]=-1
        elif (df.loc[i,"response"] !=df.loc[i,"correct_response"]):
            df.loc[i,"accuracy"]=0
        else:
            df.loc[i,"accuracy"]=df.loc[i,"accuracy"]
         
    
    df=df.drop(df.index[len(df)-1])

    return df,tail   

try:
    error_folder = csvpath
    for f in open(runsheet,'r'):    
        f=f.strip("\n")
        try:
            csv_list=extension_tsv(csvpath,f,newpath)
            for f2 in open(csvpath+"/"+f+"/eprime_csvfiles/csv_list.txt","r"):
            
                f2=f2.strip("\n")                    
                df,tail=csv_df(f2)
                num=tail[-1]
                tail1=tail.split('_')
                name = tail1[0]
                name = name.split('-')
                name = name[-1]
                name2 = name[:5]
                                       
                if not os.path.exists(newpath+"/"+ f +"/func"): 
                    os.makedirs(newpath+"/"+f +"/func") 
                df.to_csv(newpath+"/"+f+'/func/'+f+'_task-faces_run-0'+str(num)+'_events.tsv',header=True, sep='\t',mode='w',index=False)
      
            os.remove(csvpath+"/"+f+"/eprime_csvfiles/csv_list.txt")
        except:
            print('Error loading {}'.format(f))
            fi = open(error_folder + '/error_log.txt', 'a')
            fi.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'csv2tsv', f, 'load error'))
            fi.close()
except:
    pass

    
