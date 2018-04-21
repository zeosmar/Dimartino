#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 10:25:37 2018

@author: stan
"""
import os
import argparse
import sys
import os.path as path
from physio_libs import * 

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)
        
parser = MyParser(prog="proc_biopac_coins")
parser.add_argument('-project','--project_directory', help="The project folder containing sourceData, etc. (Required)", required=True)
parser.add_argument("-sublist", "--subject_list", help="File name listing subjects to process; defaults to 'subject_list.txt' in the working directory.", default='subject_list.txt')
parser.add_argument("-templates", "--template_directory", help="Directory for physio templates; defaults to 'physio_templates' in project dir", default='physio_templates')
args = parser.parse_args()

source_dir = path.abspath(path.expanduser(args.project_directory))
if args.template_directory == "physio_templates":
    template_dir = path.join(source_dir,"physio_templates")
else:
    template_dir = path.abspath(path.expanduser(source_dir))
    
sublist = [fil.strip() for fil in open(args.subject_list)]

for sub in sublist:
    print(sub.upper().strip())
    physio = PhysioObject()
    physio.subid = sub.strip()
    sub_template = path.join(template_dir, "%s_physio-template.json"%sub)
    physio.load_from_template(sub_template)
    qa_dir = os.path.join(source_dir, sub,'QC','physio')
    plot_subject_struct(physio, qa_dir)
    physio_out = os.path.join(source_dir,"BIDS")
    save_physio_tsv(physio, physio_out)
    print('')
    