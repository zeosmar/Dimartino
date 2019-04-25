#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 16:40:10 2018

@author: sray
"""

import os, sys
import pandas as pd
import numpy as np
from optparse import OptionParser
import argparse
import datetime

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

parser=MyParser(prog="DCM2BIDS")
parser.add_argument("--source",dest="source")
parser.add_argument("--destination",dest="destination")
parser.add_argument("--COINS_BIDS",dest="COINS_BIDS")

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args=parser.parse_args()

if args.source:
    heads, tails=os.path.split(args.source)
    if heads=='':
        heads=basePath
        
    fullpaths=os.path.join(heads,tails)

if args.destination:
    headd, taild=os.path.split(args.destination)
    if headd=='':
        headd=basePath
        
    fullpathd=os.path.join(headd,taild)
    
if args.COINS_BIDS:
    headc,tailc=os.path.split(args.COINS_BIDS)
    if headc=='':
        headc=basePath
        
    fullpathc=os.path.join(headc,tailc)
    coins_bids=pd.read_csv(fullpathc)

path = fullpaths.split('/')

if 'sub-' in path[-1]:
    subID = path[-1].lstrip('sub-')
    if os.path.exists(fullpaths + '/' + str(subID) + ".json"):
        cmd="dcm2bids -d " + fullpaths + " -p " + str(subID) + " -c " + fullpaths + "/" + str(subID) + ".json" + " -o " + fullpathd
        os.system(cmd)
    else:
        print('Error: subject not in source folder ' + subID)

else:
    subID=coins_bids['Scan_Subject_ID'] 
    for i in range(len(subID)):  
        if os.path.exists(fullpaths + "/sub-"+ str(subID[i]) + "/" + str(subID[i]) + ".json"):
            cmd="dcm2bids -d " + fullpaths + "/sub-" + str(subID[i]) + " -p " + str(subID[i]) + " -c " + fullpaths + "/sub-"+ str(subID[i]) + "/" + str(subID[i]) + ".json" + " -o " + fullpathd
            os.system(cmd)
        else:
            f = open(fullpaths + '/error_log.txt', 'a')
            f.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'batch_dcm2bids', subID[i], 'subject not in source folder'))
            f.close()
