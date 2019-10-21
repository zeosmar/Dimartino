#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 12:51:23 2019

@author: jcloud
"""

import os, sys
import argparse
import datetime
import shutil

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' %message)
        self.print_help()
        sys.exit(2)
        
parser=MyParser(prog="COINS_BIDS")
parser.add_argument("--bids_dir",dest="inputdir", required=True, help='BIDS input path')

args=parser.parse_args()

subjects = os.listdir(args.inputdir)

for i in range(len(subjects)):
    if 'sub-' in subjects[i]:
        sub = subjects[i]
        if len(sub) == 9:
            pass
        elif len(sub) > 9:
            new_sub = sub[:9]
            
            path = os.path.join(args.inputdir, sub)
            
            for (dirpath, dirnames, filenames) in os.walk(path):
                if 'fmap' not in dirpath:
                    for fi in filenames:
                        final_path = os.path.join(dirpath.replace(sub, new_sub), fi.replace(sub, new_sub))
                        input_path = os.path.join(dirpath, fi)
                        if not os.path.exists(dirpath.replace(sub, new_sub)):
                            os.makedirs(dirpath.replace(sub, new_sub))
                        os.rename(input_path, final_path)

            if not os.path.exists(os.path.join(args.inputdir, 'tmp_finalbids')):
                os.mkdir(os.path.join(args.inputdir, 'tmp_finalbids'))
            os.rename(path, os.path.join(args.inputdir, 'tmp_finalbids', subjects[i]))

if os.path.exists(os.path.join(args.inputdir, 'tmp_dcm2bids')):
    shutil.rmtree(os.path.join(args.inputdir, 'tmp_dcm2bids'))
if os.path.exists(os.path.join(args.inputdir, 'tmp_finalbids')):
	shutil.rmtree(os.path.join(args.inputdir, 'tmp_finalbids'))
