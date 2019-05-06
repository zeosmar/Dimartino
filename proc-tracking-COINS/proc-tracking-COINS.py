#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 12:28:38 2018

@author: jcloud
"""
# In[Info]

"""

Given a parameter -path, which points either to the main project directory or
to a single subject folder, runs preprocessing and QC on gaze and pupil data
for each .edf file.

PRODUCES:
    -.tsv file with preprocessed gaze and pupil data
    -graph of gaze data, with percentage of data that falls within each of the
    expected ROIS, as well as within the general task area
    -graph of pupil data, with percentage of data remaining following
    removal of invalid samples
    -QC .csv on subject level, population level

"""
# In[Import]

import os, argparse, sys
import tracking_lib as tl

# In[Parser]

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s/n' % message)
        self.print_help()
        sys.exit(2)
        
parser = MyParser(prog='eyetracking processing')

parser.add_argument('-project', '--project_directory', 
                    help='The project folder containing sourceData, etc. (Required)', required=True)
parser.add_argument('-sublist', '--subject_list', 
                    help='File name listing subjects to process; defaults to "subject_list.txt" in the working directory.',
                    default='subject_list.txt')
parser.add_argument('-templates', '--template_directory', 
                    help='Directory for tracking templates; defaults to "tracking_templates" in project dir', 
                    default='tracking_templates')
parser.add_argument('--bids_dir', help='BIDs directory', required=True)

args = parser.parse_args()

# In[Set Up Directories]:

project_dir = os.path.abspath(os.path.expanduser(args.project_directory))
if args.template_directory == 'tracking_templates':
    template_dir = os.path.join(project_dir, 'tracking_templates')
else:
    template_dir = os.path.abspath(os.path.expanduser(args.template_directory))
    
# In[Generate SubList]:
    
sublist = [fil.strip() for fil in open(args.subject_list)]


# In[Process]

for sub in sublist:
    print(sub.upper().strip())
    track = tl.TrackObject()
    track.subid = sub.strip()
    track.project_directory = project_dir
    sub_template = os.path.join(template_dir, '{}_tracking-template.json'.format(sub))
    track.load_from_template(sub_template)
    qa_dir = os.path.join(project_dir, sub, 'QC', 'tracking')
    if not os.path.exists(qa_dir):
        os.makedirs(qa_dir)
    track.plot_qc_graphs(track, qa_dir)
    track.save_qc_csv(track, qa_dir)
    track_out = os.path.join(project_dir, 'BIDS')
    #track.save_track_csv(track, project_dir, sub)
    track.save_track_tsv(track, args.bids_dir)
    print('')
