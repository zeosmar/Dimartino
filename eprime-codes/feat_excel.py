#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:06:46 2017

@author: sray
"""

#Import Libraries
import re
import sys
import os
import pandas as pd
import io
import numpy as np
import argparse
import datetime

class MyParser(argparse.ArgumentParser):
    def error(self,message):
        sys.stderr.write('error: %s \n' % message)
        self.print_help()
        sys.exit(2)
        
def gracefulExit():
    parser.print_help()
    exit(2)

parser = MyParser(prog="Convert .csv files into feat 3 column format")
parser.add_argument('-input_dir','--source_dir',help="The input directory path which contains the .csv files", dest = 'input_dir', required=True)
parser.add_argument('-output_dir','--bids_dir',help="Enter the output directory for the feat subject files", dest = 'output_dir', required=True)
parser.add_argument('--subject_list', required=True, help='list of subjects to process', dest = 'subject_list')

args=parser.parse_args()

if args.input_dir:
    direc=args.input_dir    
if args.output_dir:
    newpath=args.output_dir
if args.subject_list:
    f = open(args.subject_list)
    subject_list = f.read().splitlines()
    f.close()

def feat_creation_two(csvpath, outputpath, f1):
    error_folder = csvpath
    task_list = ['task-faces_run-01', 'task-faces_run-02']

    for task in task_list:
        try:
            event_file = f1 + '_' + task + '_events.tsv'
            event_folder = os.path.join(outputpath, f1, 'func', event_file)

            event_data = pd.read_csv(event_folder, sep='\t')
        except IOError:
            print('Error loading {}'.format(f1))
            fi = open(error_folder + '/error_log.txt', 'a')
            fi.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'feat_excel', f, 'no tsv file found'))
            fi.close()
            continue
        
        all_shape = event_data[event_data['procedure'] == 'Shape']
        all_face = event_data[event_data['procedure'] == 'Face']

        acc_shape = event_data[np.logical_and(event_data['procedure'] == 'Shape', event_data['accuracy'] == 1)]
        inacc_shape = event_data[np.logical_and(event_data['procedure'] == 'Shape', event_data['accuracy'] == 0)]
        acc_face = event_data[np.logical_and(event_data['procedure'] == 'Face', event_data['accuracy'] == 1)]
        inacc_face = event_data[np.logical_and(event_data['procedure'] == 'Face', event_data['accuracy'] == 0)]

        event_data = event_data[['onset', 'duration', 'procedure']]
        for x in range(len(event_data)):
            if event_data['procedure'][x] == 'Shape':
                event_data.loc[x, 'procedure'] = 0
            else:
                event_data.loc[x, 'procedure'] = 1

        outpath = os.path.join(outputpath, f1, 'feat')
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        
        ones = np.ones(len(all_shape))
        all_shape['procedure'] = ones
        all_shape.to_csv(outpath + '/' + f1 + '_' + task + '_shapes.txt', sep='\t', columns=['onset', 'duration', 'procedure'], index=None, header=None)

        ones = np.ones(len(all_face))
        all_face['procedure'] = ones
        all_face.to_csv(outpath + '/' + f1 + '_' + task + '_faces.txt', sep='\t', columns=['onset', 'duration', 'procedure'], index=None, header=None)

        ones = np.ones(len(acc_shape))
        acc_shape['procedure'] = ones
        acc_shape.to_csv(outpath + '/' + f1 + '_' + task + '_shapes-correct.txt', sep='\t', columns=['onset', 'duration', 'procedure'], index=None, header=None)

        ones = np.ones(len(inacc_shape))
        inacc_shape['procedure'] = ones
        inacc_shape.to_csv(outpath + '/' + f1 + '_' + task + '_shapes-incorrect.txt', sep='\t', columns=['onset', 'duration', 'procedure'], index=None, header=None)

        ones = np.ones(len(acc_face))
        acc_face['procedure'] = ones
        acc_face.to_csv(outpath + '/' + f1 + '_' + task + '_faces-correct.txt', sep='\t', columns=['onset', 'duration', 'procedure'], index=None, header=None)

        ones = np.ones(len(inacc_face))
        inacc_face['procedure'] = ones
        inacc_face.to_csv(outpath + '/' + f1 + '_' + task + '_faces-incorrect.txt', sep='\t', columns=['onset', 'duration', 'procedure'], index=None, header=None)

        event_data.to_csv(outpath + '/' + f1 + '_' + task + '_all.txt', sep='\t', index=None, header=None)

def feat_creation(csvpath,f1):
    try:
        error_folder = csvpath
        cmd="ls "+ csvpath + "/"+f1+ "/eprime_csvfiles"+"/*.csv > " +csvpath + "/" + f1 + "/eprime_csvfiles/csvfilelist.txt"
        os.system(cmd)
        
        #path to store the participant response accuracy % data
        csvfilelist=open(csvpath+"/"+f1+"/eprime_csvfiles/csvfilelist.txt")
        run_count=0
        if os.stat(csvpath+"/"+f1+"/eprime_csvfiles/csvfilelist.txt").st_size!=0:
            for f in csvfilelist:
                f=f.strip("\n")
                acc_f=open(path+"/"+"subj_acc.txt","a")
                
                #readrequired columns
                df = pd.read_csv(f, usecols=['SyncSlide.OnsetTime','Procedure','ExperimenterWindow.OnsetTime','StimSlide.OnsetToOnsetTime','StimSlide.OnsetTime','StimSlide.RESP','StimSlide.ACC','StimSlide.CRESP','StimSlide.RT'])
                csv1=f.strip(".csv")
                head,tail=os.path.split(csv1)
                run_count=run_count+1 
                
                #Calculate Onset Time with respect to reference
                ref_p=df.loc[0,"SyncSlide.OnsetTime"]/1000
                b=ref_p
                df['ReferencePoint']=b
                df["Onset"]=0
                for i in range(len(df)):
                    if (pd.isnull(df.loc[i,"StimSlide.OnsetTime"])):
                        df.loc[i,"StimSlide.OnsetTime"]=df.loc[i,"StimSlide.OnsetTime"]
                    else:
                        df.loc[i,"StimSlide.OnsetTime"]=df.loc[i,"StimSlide.OnsetTime"]/1000
                        df.loc[i,"Onset"]=df.loc[i,"StimSlide.OnsetTime"]-df.loc[i,"ReferencePoint"]
                
                # remove rows not required and reindex
                df=df[df.Procedure != "InitialTR"]  
                df=df[df.Procedure != "TwoSecFixPROC"]  
                df=df.reset_index(drop=True)    
                
                # rename trial types with either face/shape trial  
                new_index=(0,len(df))
                df.reindex(new_index)
                for i in range(0,len(df),7):
                    if(df.loc[i,"Procedure"] =="ShapePromptPROC"):
                        for j in range(1,7):
                            a=i+j
                            df.loc[a,"Procedure"]="Shape" 
                    elif(df.loc[i,"Procedure"] =="FacePromptPROC"):
                        for j in range(1,7):
                            a=i+j
                            df.loc[a,"Procedure"]="Face"
                    else:
                        df.loc[i,"Procedure"]=df.loc[i,"Procedure"]
                
                #Eliminate rows not required and rename null data to "n/a"
                df=df[df.Procedure != "ShapePromptPROC"]
                df=df[df.Procedure != "FacePromptPROC"]
                df["StimSlide.OnsetToOnsetTime"]=df["StimSlide.OnsetToOnsetTime"]/1000
                df["Duration"]=df["StimSlide.OnsetToOnsetTime"]
                df["StimSlide.RT"]=df["StimSlide.RT"]/1000
            
                df.loc[df["StimSlide.OnsetTime"].isnull(),"StimSlide.OnsetTime"]="n/a"
            
                df.loc[df["ExperimenterWindow.OnsetTime"].isnull(),"ExperimenterWindow.OnsetTime"]="n/a"
                df.loc[df['StimSlide.OnsetToOnsetTime'].isnull(),'StimSlide.OnsetToOnsetTime']="n/a"
                df.loc[df["Procedure"].isnull(),"Procedure"]="n/a"
                df.loc[df["StimSlide.RESP"].isnull(),"StimSlide.RESP"]="n/a"
                df.loc[df["StimSlide.ACC"].isnull(),"StimSlide.ACC"]="n/a"
                df.loc[df["StimSlide.CRESP"].isnull(),"StimSlide.CRESP"]="n/a"
                df.loc[df["Duration"].isnull(),"Duration"]="n/a"
                df.loc[df["StimSlide.RT"].isnull(),"StimSlide.RT"]="n/a"
            
                #Delete Columns not required and reindex again
                del df["SyncSlide.OnsetTime"]
                del df["ExperimenterWindow.OnsetTime"]
                del df["ReferencePoint"]
                df=df[["Onset","Duration","Procedure","StimSlide.RT","StimSlide.ACC","StimSlide.RESP","StimSlide.CRESP"]]
                df=df.reset_index(drop=True)
                df=df.drop(df.index[len(df)-1])
                
                #Count number of Shape and Face trial data and allocate dataframe memory for each
                s_c=0
                f_c=0
                s_rt=0
                f_rt=0

                for i in range(0,len(df)):
                    try:
                        if (df.loc[i,"Procedure"]=="Shape"):
                            s_c=s_c+1
                            s_rt=s_rt + float(df["StimSlide.RT"][i])
                        elif (df.loc[i,"Procedure"]=="Face"):
                            f_c=f_c+1                    
                            f_rt=f_rt+float(df["StimSlide.RT"][i])
                        else:
                            continue
                    except:
                        continue
                df_s=pd.DataFrame(np.zeros(s_c))
                df_f=pd.DataFrame(np.zeros(f_c))
                df_s["Procedure"]=0
                df_s["Onset"]=0
                df_s["Duration"]=0
                df_s["Wait"]=0
                df_s["StimSlide.ACC"]=0
                df_s["StimSlide.RESP"]=0
                df_s["StimSlide.CRESP"]=0
                df_f["Procedure"]=0
                df_f["Onset"]=0
                df_f["Duration"]=0
                df_f["Wait"]=0
                df_f["StimSlide.ACC"]=0
                df_f["StimSlide.RESP"]=0
                df_f["StimSlide.CRESP"]=0   
                
                #Seperate Shape and Face trials
                j=0
                k=0
                acc_c_shape=0
                acc_w_shape=0
                acc_c_face=0
                acc_w_face=0
                for i in range(0,len(df)):
                    if (df.loc[i,"Procedure"]=="Shape"):
                              
                        df_s.loc[j,"Procedure"]=df.loc[i,"Procedure"]
                        df_s.loc[j,"Onset"]=df.loc[i,"Onset"]
                        df_s.loc[j,"Duration"]=df.loc[i,"Duration"]
                        df_s.loc[j,"Wait"]=1
                        df_s.loc[j,"StimSlide.ACC"]=df.loc[i,"StimSlide.ACC"]
                        df_s.loc[j,"StimSlide.RESP"]=df.loc[i,"StimSlide.RESP"]
                        df_s.loc[j,"StimSlide.CRESP"]=df.loc[i,"StimSlide.CRESP"]
                        j=j+1
                        if (df.loc[i,"StimSlide.RESP"]==df.loc[i,"StimSlide.CRESP"]):
                            acc_c_shape=acc_c_shape+1
                        elif (df.loc[i,"StimSlide.RESP"]=="n/a"):
                            continue
                        elif (df.loc[i,"StimSlide.RESP"]!=df.loc[i,"StimSlide.CRESP"]):
                            acc_w_shape=acc_w_shape+1
                                
                    else:
                       
                        df_f.loc[k,"Procedure"]=df.loc[i,"Procedure"]
                        df_f.loc[k,"Onset"]=df.loc[i,"Onset"]
                        df_f.loc[k,"Duration"]=df.loc[i,"Duration"]
                        df_f.loc[k,"Wait"]=1
                        df_f.loc[k,"StimSlide.ACC"]=df.loc[i,"StimSlide.ACC"]
                        df_f.loc[k,"StimSlide.RESP"]=df.loc[i,"StimSlide.RESP"]
                        df_f.loc[k,"StimSlide.CRESP"]=df.loc[i,"StimSlide.CRESP"]
                        k=k+1
                        if (df.loc[i,"StimSlide.RESP"]==df.loc[i,"StimSlide.CRESP"]):
                            acc_c_face=acc_c_face+1
                        elif (df.loc[i,"StimSlide.RESP"]=="n/a"):
                            continue
                        elif (df.loc[i,"StimSlide.RESP"]!=df.loc[i,"StimSlide.CRESP"]):
                            acc_w_face=acc_w_face+1
                
                newpath1=newpath+"/"+ f1 + '/feat'
                if not os.path.exists(newpath1):
                    os.makedirs(newpath1)
                
                #Calculate accuracy % for shape or face response
                shape_r=pd.DataFrame(np.zeros(acc_c_shape))
                shape_w=pd.DataFrame(np.zeros(acc_w_shape))
                shape_r["Procedure"]=0
                shape_r["Onset"]=0
                shape_r["Duration"]=0
                shape_r["Wait"]=0
                shape_r["StimSlide.ACC"]=0
                shape_w["Procedure"]=0
                shape_w["Onset"]=0
                shape_w["Duration"]=0
                shape_w["Wait"]=0
                shape_w["StimSlide.ACC"]=0
                l=0
                m=0
                
                for i in range(0,len(df_s)):
                    if df_s.loc[i,"StimSlide.RESP"]==df_s.loc[i,"StimSlide.CRESP"]:
                        shape_r.loc[l,"Procedure"]=df_s.loc[i,"Procedure"]
                        shape_r.loc[l,"Onset"]=df_s.loc[i,"Onset"]
                        shape_r.loc[l,"Duration"]=df_s.loc[i,"Duration"]
                        shape_r.loc[l,"Wait"]=df_s.loc[i,"Wait"]
                        shape_r.loc[l,"StimSlide.ACC"]=1          
                        l=l+1
                    elif df_s.loc[i,"StimSlide.RESP"]=="n/a":
                        continue
                    elif df_s.loc[i,"StimSlide.RESP"]!=df_s.loc[i,"StimSlide.CRESP"]:
                        shape_w.loc[m,"Procedure"]=df_s.loc[i,"Procedure"]
                        shape_w.loc[m,"Onset"]=df_s.loc[i,"Onset"]
                        shape_w.loc[m,"Duration"]=df_s.loc[i,"Duration"]
                        shape_w.loc[m,"Wait"]=df_s.loc[i,"Wait"]
                        shape_w.loc[m,"StimSlide.ACC"]=0
                        m=m+1
                                    
                face_r=pd.DataFrame(np.zeros(acc_c_face))
                face_w=pd.DataFrame(np.zeros(acc_w_face))
                face_r["Procedure"]=0
                face_r["Onset"]=0
                face_r["Duration"]=0
                face_r["Wait"]=0
                face_r["StimSlide.ACC"]=0
                face_w["Procedure"]=0
                face_w["Onset"]=0
                face_w["Duration"]=0
                face_w["Wait"]=0
                face_w["StimSlide.ACC"]=0
                n=0
                p=0
                
                for i in range(0,len(df_f)):
                    if df_f.loc[i,"StimSlide.RESP"]==df_f.loc[i,"StimSlide.CRESP"]:
                        face_r.loc[n,"Procedure"]=df_f.loc[i,"Procedure"]
                        face_r.loc[n,"Onset"]=df_f.loc[i,"Onset"]
                        face_r.loc[n,"Duration"]=df_f.loc[i,"Duration"]
                        face_r.loc[n,"Wait"]=df_f.loc[i,"Wait"]
                        face_r.loc[n,"StimSlide.ACC"]=1          
                        n=n+1
                    elif df_f.loc[i,"StimSlide.RESP"]=="n/a":
                        continue
                    elif df_f.loc[i,"StimSlide.RESP"]!=df_f.loc[i,"StimSlide.CRESP"]:
                        face_w.loc[p,"Procedure"]=df_f.loc[i,"Procedure"]
                        face_w.loc[p,"Onset"]=df_f.loc[i,"Onset"]
                        face_w.loc[p,"Duration"]=df_f.loc[i,"Duration"]
                        face_w.loc[p,"Wait"]=df_f.loc[i,"Wait"]
                        face_w.loc[p,"StimSlide.ACC"]=0
                        p=p+1
                        
                shape_c_write=shape_r[["Onset","Duration","Wait"]]
                shape_w_write=shape_w[["Onset","Duration","Wait"]]
                face_c_write=face_r[["Onset","Duration","Wait"]]
                face_w_write=face_w[["Onset","Duration","Wait"]]
                
                name = f1[:9]
                
                #Save the data in separate .txt files    
                shape_c_write.to_csv(newpath+"/"+f1+"/feat/"+name+"_shape_correct.txt",header=False, sep=' ',mode='w',index=False)     
                shape_w_write.to_csv(newpath+"/"+f1+"/feat/"+name+"_shape_incorrect.txt",header=False, sep=' ',mode='w',index=False)     
                face_c_write.to_csv(newpath+"/"+f1+"/feat/"+name+"_face_correct.txt",header=False, sep=' ',mode='w',index=False)     
                face_w_write.to_csv(newpath+"/"+f1+"/feat/"+name+"_face_incorrect.txt",header=False, sep=' ',mode='w',index=False)     
                
                #stores each subject trial response
                if run_count==1:
                    face_accuracy_p1=round((float(acc_c_face)/f_c)*100,3)                                    
                    shape_accuracy_p1=round((float(acc_c_shape)/s_c)*100,3)

                    total_shape_face_p1=f_c+s_c
                    total_acc_p1=acc_c_face+acc_c_shape
                    overall_acc_p1=round((float(total_acc_p1)/total_shape_face_p1)*100,3)

                    face_rt_avg1=round((float(f_rt)/f_c),3)
                    shape_rt_avg1=round((float(s_rt)/s_c),3)
                    
                else:
                    face_accuracy_p2=round((float(acc_c_face)/f_c)*100,3)
                    shape_accuracy_p2=round((float(acc_c_shape)/s_c)*100,3)

                    total_shape_face_p2=f_c+s_c
                    total_acc_p2=acc_c_face+acc_c_shape
                    overall_acc_p2=round((float(total_acc_p2)/total_shape_face_p2)*100,3)

                    face_rt_avg2=round((float(f_rt)/f_c),3)
                    shape_rt_avg2=round((float(s_rt)/s_c),3)
                    
                    acc_f.write(f1 + "\t" + str('{:.3f}'.format(face_rt_avg1)) + "\t" + str('{:.3f}'.format(shape_rt_avg1)) + "\t" + str('{:.3f}'.format(face_rt_avg2)) + "\t" + str('{:.3f}'.format(shape_rt_avg2)) + " \t \t" + str('{:.3f}'.format(face_accuracy_p1)) + "\t" + str('{:.3f}'.format(shape_accuracy_p1)) + "\t" + str('{:.3f}'.format(face_accuracy_p2)) + "\t" + str('{:.3f}'.format(shape_accuracy_p2))+ "\t \t" + str('{:.3f}'.format(overall_acc_p1)) + "\t " + str('{:.3f}'.format(overall_acc_p2))+"\n")       
            
            acc_f.close()
            os.remove(csvpath+"/"+f1+"/eprime_csvfiles/csvfilelist.txt")
        else:
            print('Error loading {}'.format(f1))
            fi = open(error_folder + '/error_log.txt', 'a')
            fi.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'feat_excel', f1, 'no csv files for this subject'))
            fi.close()
    except:
        print('Error loading {}'.format(f1))
        fi = open(error_folder + '/error_log.txt', 'a')
        fi.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'feat_excel', f1, 'load error'))
        fi.close()


os.chdir(newpath)
path=os.getcwd()    
csvpath=direc
if os.path.isfile(path+"/"+"subj_acc.txt")!=True:        
    acc_f=open(path+"/"+"subj_acc.txt","a")
    acc_f.write("SubjectID \t Reaction_Time \t " +  "\t \t \t \t %_Accuracy" +  " \t \t \t \t \t %_Overall Accuracy \n")
    acc_f.write("\t Run_1 \t \t Run_2" + "\t  \t \t Run_1 \t \t Run_2 \n")
    acc_f.write(" \t Face \t Shape " + " \t Face \t Shape \t \t Face \t Shape \t Face \t Shape "+ "\t \t Run_1 \t Run_2 \n")
    acc_f.close()             
for f1 in subject_list:
    f1=f1.strip("\n")
    #feat_creation(csvpath,f1)
    feat_creation_two(csvpath, newpath, f1)


