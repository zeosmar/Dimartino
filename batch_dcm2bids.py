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
    
subID=pd.DataFrame(coins_bids.iloc[:,1])

for i in range(len(subID)):    
    cmd="/usr/local/Anaconda2/bin/dcm2bids -d " + fullpaths + "/sub-" + str(subID["subID"][i]) + " -p " + str(subID["subID"][i]) + " -c " + fullpaths + "/sub-"+ str(subID["subID"][i]) + "/" + str(subID["subID"][i]) + ".json" + " -o " + fullpathd
    os.system(cmd)