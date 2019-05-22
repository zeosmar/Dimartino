#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 17 22:10:22 2017

@author: sray
"""

#import required libraries
import sys
import os
import convert_eprime as ce
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
    
#Accept input at command line window
parser = MyParser(prog="Convert eprime .txt to .csv")
parser.add_argument('-path','--source_dir',help="input directory with subject folders having eprime data", dest = 'path', required = True)
parser.add_argument('--subject_list', required = True, help="List of subjects to process")

#check if required number of arguments have been passed
if len(sys.argv)==0:
    parser.print_help()
    sys.exit(1)
    
args=parser.parse_args()

if args.path:
    direc=args.path
    error_folder = direc
    path=os.chdir(direc)

if args.subject_list:
    f = open(args.subject_list)
    subject_list = f.read().splitlines()
    f.close()

    for f in subject_list:
        txtpath=direc+"/"+f+"/originals/01+ePrimeData"
        try:
            os.chdir(txtpath)
            cmd2="ls | grep run1.txt > eprime_txt_list.txt" 
            os.system(cmd2)
            for f1 in open("eprime_txt_list.txt"):
                f1=f1.strip("\n")
                fname,ext=os.path.splitext(f1)
                fname_2=fname[:-13] 
                file_name=fname_2[:-6] 
                out_file=direc +"/"+ f+"/eprime_csvfiles/"+fname_2+".csv" 
                txtfile=direc+"/"+f+"/originals/01+ePrimeData/"+f1
                if not os.path.exists(direc +"/"+ f+"/eprime_csvfiles"): 
                    os.makedirs(direc +"/"+ f+"/eprime_csvfiles") 
                ce.text_to_csv(f1, out_file)
        except:
            print('Error loading {}'.format(f))
            fi = open(error_folder + '/error_log.txt', 'a')
            fi.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'batch_ce', f, 'load error'))
            fi.close()
        

