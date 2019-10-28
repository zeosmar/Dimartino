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
from physio_libs2 import * 

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)
        
parser = MyParser(prog="proc_biopac_coins")
parser.add_argument('-project','--source_dir', help="The project folder containing sourceData, etc. (Required)", required=True, dest='project_directory')
parser.add_argument("-sublist", "--subject_list", help="File name listing subjects to process; defaults to 'subject_list.txt' in the working directory.", default='subject_list.txt')
parser.add_argument("-templates", "--template_directory", help="Directory for physio templates; defaults to 'physio_templates' in project dir", default='physio_templates')
parser.add_argument('--bids_dir', help='BIDs directory', required=True)
args = parser.parse_args()

project_dir = path.abspath(path.expanduser(args.project_directory))
if args.template_directory == "physio_templates":
    template_dir = path.join(project_dir,"physio_templates")
else:
    template_dir = path.abspath(path.expanduser(args.template_directory))
    
sublist = [fil.strip() for fil in open(args.subject_list)]

for sub in sublist:
    print(sub.upper().strip())
    physio = PhysioObject()
    physio.subid = sub.strip()
    physio.project_directory = project_dir
    sub_template = path.join(template_dir, "%s_physio-template.json"%sub)
    physio.load_from_template(sub_template)
    qa_dir = os.path.join(project_dir, sub,'QC','physio')
    #plot_subject_struct(physio, qa_dir)
    #plot_subject_rr(physio, qa_dir)
    #plot_subject_hr_peaks(physio, qa_dir)
    plot_subject_rr_peaks(physio, qa_dir)
    #pulse_boxplot(physio, qa_dir)
    #resp_boxplot(physio, qa_dir)
    #boxplot_1min(physio, qa_dir)
    #heart_resp_all(physio, qa_dir)
    #stability(physio, qa_dir)
    
    physio_out = os.path.join(project_dir,"BIDS")
    save_physio_csv_rest1_rr(physio, project_dir)
    #save_physio_tsv(physio, args.bids_dir)
    print('')
    
