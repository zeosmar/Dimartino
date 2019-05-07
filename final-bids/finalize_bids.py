#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 12:51:23 2019

@author: jcloud
"""

import os, sys
import argparse
import datetime

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' %message)
        self.print_help()
        sys.exit(2)
        
parser=MyParser(prog="COINS_BIDS")
parser.add_argument("--bids_dir",dest="inputdir", required=True, help='BIDS input path')

args=parser.parse_args()

subjects = os.listdir(args.inputdir)

duplicates = {}

for i in range(len(subjects)):
    if 'sub-' in subjects[i]:
        sub = subjects[i]
        if len(sub) == 9:
            duplicates[sub] = []
        elif len(sub) > 9:
            try:
                duplicates[sub[:9]].append(sub)
            except KeyError:
                pass

for sub in duplicates:
    if len(duplicates[sub]) > 0:
        path = os.path.join(args.inputdir, sub)
        f = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            f.extend(filenames)
            
        for i in duplicates[sub]:
            path2 = os.path.join(args.inputdir, i)
            
            for (dirpath, dirnames, filenames) in os.walk(path2):
                if 'fmap' not in dirpath:
                    for fi in filenames:
                        final_path = os.path.join(dirpath.replace(i, sub), fi.replace(i, sub))
                        input_path = os.path.join(dirpath, fi)
                        if not os.path.exists(dirpath.replace(i, sub)):
                            os.makedirs(dirpath.replace(i, sub))
                        os.rename(input_path, final_path)

            if not os.path.exists(os.path.join(args.inputdir, 'tmp_finalbids')):
                os.mkdir(os.path.join(args.inputdir, 'tmp_finalbids'))
            os.rename(path2, os.path.join(args.inputdir, 'tmp_finalbids', i))
    
        
