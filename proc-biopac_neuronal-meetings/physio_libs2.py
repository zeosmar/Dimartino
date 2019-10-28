#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 10:05:12 2018

@author: stan
"""

#clean up file names/parameter inputs to match each other
#adapt to weird naming schemes in batch_ce (eprime files named different)
#output error files with subject nums of failed runs, rough description of reason
#clean up and comment some of the code for clarity
#look at dcmnixx 2.0 - what's new/different in that code
from __future__ import division
import bioread as br
import numpy as np
import scipy.signal as signal
import scipy.stats as stats
from scipy.stats import kurtosis
from scipy.stats import skew as skewness
import os.path as path
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import ticker
import seaborn as sns
import pandas as pd
import datetime

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

# Yield successive n-sized 
# chunks from l. 
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n]

class PhysData():
    def __init__(self):
        self.pulse = np.nan
        self.resp = np.nan
        self.hr = np.nan
        self.rr = np.nan 
        self.hr_std = np.nan
        self.rr_std = np.nan
        self.hr_cv = np.nan
        self.rr_cv = np.nan
        self.hr_idx = np.nan
        self.rr_idx = np.nan
        self.pulse_kurt = np.nan
        self.pulse_skew = np.nan
        self.resp_kurt = np.nan
        self.resp_skew = np.nan
        self.pulse_perc = np.nan
        self.resp_perc = np.nan
        self.pulse_perc_above = np.nan
        self.resp_perc_above = np.nan
        self.min1_pulse = np.nan
        self.min1_resp = np.nan
        self.min1_skew_pulse = np.nan
        self.min1_kurt_pulse = np.nan
        self.min1_skew_resp = np.nan
        self.min1_kurt_resp = np.nan
        self.pulse_skew_perc = np.nan
        self.pulse_skew_perc_above = np.nan
        self.pulse_kurt_perc = np.nan
        self.pulse_kurt_perc_above = np.nan
        self.resp_skew_perc = np.nan
        self.resp_skew_perc_above = np.nan
        self.resp_kurt_perc = np.nan
        self.resp_kurt_perc_above = np.nan
        self.pulse_perc_green = np.nan
        self.resp_perc_green = np.nan
        self.pulse_blocks = np.nan
        self.name = ""

class PhysioObject():
    def __init__(self):
        self.subid = ""
        self.project_directory = ""
        self.tasklist = ['face1', 'face2', 'rest1', 'rest2']
        self.target_sampling_rate = 50
        self.natve_sampling_rate = np.nan
        self.hasloaded = False
        self.run = {}
        for task in self.tasklist:
            self.run[task] = PhysData()

    def write_to_missing(self, filepath, taskname):
        logpath = path.join(self.project_directory, "missing_physio_runs.csv")
        if path.exists(logpath) is False:
            f = open(logpath, 'w')
            f.write('subject,fmri,date_time,coins_path\n')
            f.close()
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        outstr = "%s,%s,%s,%s\n"%(self.subid, taskname, datestr, filepath)
        f = open(logpath, 'a')
        f.write(outstr)
        f.close()
            
    @staticmethod
    def get_channels(acq):
        trig = np.nan
        pulse = np.nan
        resp = np.nan
        pulse_str = u'PPG100C'
        trigger_str = u'Digital input'
        resp_str = u'Custom, DA100C'
        for k in range(len(acq.channels)):
            cname = acq.channels[k].name
            if "TRIGGER" in cname or trigger_str in cname:
                trig = acq.channels[k].data
            elif "PULSE" in cname or pulse_str in cname:
                pulse = acq.channels[k].data
            elif "RESP" in cname or resp_str in cname:
                resp = acq.channels[k].data
        idx = np.where(trig)
        pulse = pulse[idx]
        resp = resp[idx]
        return(pulse, resp, idx[0])
        
    def load_from_template(self,infile):
        infile = path.abspath(path.expanduser(infile))
        error_folder = infile.split('/')
        error_folder = '/'.join(error_folder[:-2])
        if path.isfile(infile):
            with open(infile) as json_data:
                d = json.load(json_data)
            for task in self.tasklist:
                taskfile = path.abspath(path.expanduser(d[task]))
                if d[task] != '' and path.isfile(taskfile):
                    print("loading: %s"%taskfile)
                    data = br.read_file(taskfile)
                    try:
                        print("loading: %s"%taskfile)
                        data = br.read_file(taskfile)
                        pulse, resp, idx = self.get_channels(data)
                        self.run[task].resp = resp
                        self.run[task].pulse= pulse
                    except:
                        print('Error loading {}, {}'.format(self.subid, task))
                        f = open(error_folder + '/error_log.txt', 'a')
                        f.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'proc-biopac-coins', self.subid, 'load error'))
                        f.close()
                    try:
                        print("Processing: %s, %s"%(self.subid, task))
                        self.samples_per_second = int(data.samples_per_second)
                        #print self.samples_per_second
                        self.run[task].pulse = signal.medfilt(self.run[task].pulse,3)
                        self.run[task].resp = signal.medfilt(self.run[task].resp,3) 
                        if self.samples_per_second != self.target_sampling_rate:
                            scale = int(self.samples_per_second / self.target_sampling_rate)
                            self.run[task].pulse = signal.decimate(self.run[task].pulse,scale,zero_phase=True)
                            self.run[task].resp = signal.decimate(self.run[task].resp,scale,zero_phase=True)

                        ######  Compute the Pulse Rate
                        self.run[task].hr_idx = signal.find_peaks_cwt(self.run[task].pulse, np.arange(1,35))
                        self.run[task].hr = int(len(self.run[task].hr_idx) / ((len(self.run[task].pulse)/self.target_sampling_rate)/60.0))
                        print(len(self.run[task].hr_idx))
                        hr_list = []
                        cnt=0
                        
                        while (cnt < (len(self.run[task].hr_idx)-1)):
                            hr_interval = (self.run[task].hr_idx[cnt+1] - self.run[task].hr_idx[cnt])
                            ms_dist = ((hr_interval/50.0)*1000)
                            #print (ms_dist)
                            if ms_dist < 0.1:
                                ms_dist=float('nan')
                            hr_list.append(ms_dist)
                            cnt += 1
                        
                        self.run[task].pulse_bpm = [60000 / x for x in hr_list]
                        #self.bpm_mean = 60000/np.mean(hr_list)

                        self.run[task].pulse_bpm = np.round(self.run[task].pulse_bpm)
                        #print (self.run[task].pulse_bpm)
                        self.run[task].pulse_skew=np.round(skewness(self.run[task].pulse_bpm,nan_policy='omit'),3)
                        self.run[task].pulse_kurt=np.round(kurtosis(self.run[task].pulse_bpm,nan_policy='omit'),3)
                        
                        ###########################
                        if "rest1" in task:
                            self.run[task].min1_pulse = np.array_split(self.run[task].pulse_bpm, 6)
                            self.run[task].min1_skew_pulse = []
                            self.run[task].min1_kurt_pulse = []
                            for i in range(len(self.run[task].min1_pulse)):
                                self.run[task].min1_skew_pulse.append(np.round(skewness(self.run[task].min1_pulse[i],nan_policy='omit'),3))
                                self.run[task].min1_kurt_pulse.append(np.round(kurtosis(self.run[task].min1_pulse[i],nan_policy='omit'),3))
                            # print(self.run[task].min1_kurt_pulse)
                            # print(self.run[task].min1_skew_pulse)
                            min1_std2neg_skew = np.mean(self.run[task].min1_skew_pulse) - 1 * np.std(self.run[task].min1_skew_pulse)
                            min1_std2pos_skew = np.mean(self.run[task].min1_skew_pulse) + 1 * np.std(self.run[task].min1_skew_pulse)
                            min1_std2neg_kurt = np.mean(self.run[task].min1_kurt_pulse) - 1 * np.std(self.run[task].min1_kurt_pulse)
                            min1_std2pos_kurt = np.mean(self.run[task].min1_kurt_pulse) + 1 * np.std(self.run[task].min1_kurt_pulse)
                            count_pass_skew = ((min1_std2neg_skew < self.run[task].min1_skew_pulse) & (self.run[task].min1_skew_pulse < min1_std2pos_skew)).sum()
                            count_fail_skew = ((min1_std2neg_skew > self.run[task].min1_skew_pulse) & (self.run[task].min1_skew_pulse > min1_std2pos_skew)).sum()
                            count_pass_kurt = ((min1_std2neg_kurt < self.run[task].min1_kurt_pulse) & (self.run[task].min1_kurt_pulse < min1_std2pos_kurt)).sum()
                            count_fail_kurt = ((min1_std2neg_kurt > self.run[task].min1_kurt_pulse) & (self.run[task].min1_kurt_pulse > min1_std2pos_kurt)).sum()
                            total_skew = len(self.run[task].min1_skew_pulse); total_kurt = len(self.run[task].min1_kurt_pulse)
                            self.run[task].pulse_skew_perc = np.round((count_pass_skew/total_skew)*100,1)
                            self.run[task].pulse_skew_perc_above = np.round((count_fail_skew/total_skew)*100,1)
                            self.run[task].pulse_kurt_perc = np.round((count_pass_kurt/total_kurt)*100,1)
                            self.run[task].pulse_kurt_perc_above = np.round((count_fail_kurt/total_kurt)*100,1)

                            std2neg = np.mean(self.run[task].pulse_bpm) - 2 * np.std(self.run[task].pulse_bpm)
                            std2pos = np.mean(self.run[task].pulse_bpm) + 2 * np.std(self.run[task].pulse_bpm)
                            count_pass = ((std2neg < self.run[task].pulse_bpm) & (self.run[task].pulse_bpm < std2pos)).sum()
                            count_fail = ((std2neg > self.run[task].pulse_bpm) & (self.run[task].pulse_bpm > std2pos)).sum()
                            total = len(self.run[task].pulse_bpm)
                            self.run[task].pulse_perc = np.round((count_pass/total)*100,1)
                            self.run[task].pulse_perc_above = np.round((count_fail/total)*100,1)

                            
                            ##### Percentage of Heart Rate between 60 and 100
                            #print(self.run[task].pulse_bpm)
                            green_range = filter(lambda x: x>60 and x<130,self.run[task].pulse_bpm)
                            self.run[task].pulse_perc_green = np.round((len(green_range)/total)*100,1)
                            self.run[task].hr_std = np.round(np.nanstd(self.run[task].pulse_bpm),1)
                            self.run[task].hr_cv = np.round((self.run[task].hr_std/self.run[task].hr),1)
                            print('total: ',total)
                            print('len: ',len(green_range))
                            print('perc: ',self.run[task].pulse_perc_green)
                            print('std: ',self.run[task].hr_std)
                            print('cv:', self.run[task].hr_cv)

                            n_samples = 18
                            self.run[task].pulse_blocks = list(divide_chunks(self.run[task].pulse_bpm, n_samples))
                                   
                        #self.run[task].pulse_bpm = [0 if x == np.nan else x for x in self.run[task].pulse_bpm]
                        #self.run[task].pulse_bpm[np.isnan(self.run[task].pulse_bpm)]=0
                        
                        ######  Compute the Resp Rate
                        self.run[task].rr_idx = signal.find_peaks_cwt(moving_average(self.run[task].resp,50), np.arange(1,70))
                        self.run[task].rr = int(len(self.run[task].rr_idx) / ((len(self.run[task].resp)/self.target_sampling_rate)/60.0))
                        rr_list = []
                        cnt=0
                        
                        while (cnt < (len(self.run[task].rr_idx)-1)):
                            rr_interval = (self.run[task].rr_idx[cnt+1] - self.run[task].rr_idx[cnt])
                            ms_dist = ((rr_interval/50.0)*1000)
                            if ms_dist < 0.1:
                                ms_dist=float('nan')
                            rr_list.append(ms_dist)
                            cnt += 1
                            
                        self.run[task].resp_bpm = [60000 / x for x in rr_list]
                        #self.bpm_mean = 60000/np.mean(rr_list)
                        self.run[task].resp_bpm = np.round(self.run[task].resp_bpm)

                        self.run[task].resp_skew=np.round(skewness(self.run[task].resp_bpm,nan_policy='omit'),3)
                        self.run[task].resp_kurt=np.round(kurtosis(self.run[task].resp_bpm,nan_policy='omit'),3)
                        ###########################
                        if "rest1" in task:
                            self.run[task].min1_resp = np.array_split(self.run[task].resp_bpm, 6)
                            self.run[task].min1_skew_resp = []
                            self.run[task].min1_kurt_resp = []
                            for i in range(len(self.run[task].min1_resp)):
                                self.run[task].min1_skew_resp.append(np.round(skewness(self.run[task].min1_resp[i],nan_policy='omit'),3))
                                self.run[task].min1_kurt_resp.append(np.round(kurtosis(self.run[task].min1_resp[i],nan_policy='omit'),3))
                            #print(self.run[task].min1_kurt_resp)
                            #print(self.run[task].min1_skew_resp)
                            min1_std2neg_skew = np.mean(self.run[task].min1_skew_resp) - 1 * np.std(self.run[task].min1_skew_resp)
                            min1_std2pos_skew = np.mean(self.run[task].min1_skew_resp) + 1 * np.std(self.run[task].min1_skew_resp)
                            min1_std2neg_kurt = np.mean(self.run[task].min1_kurt_resp) - 1 * np.std(self.run[task].min1_kurt_resp)
                            min1_std2pos_kurt = np.mean(self.run[task].min1_kurt_resp) + 1 * np.std(self.run[task].min1_kurt_resp)
                            count_pass_skew = ((min1_std2neg_skew < self.run[task].min1_skew_resp) & (self.run[task].min1_skew_resp < min1_std2pos_skew)).sum()
                            count_fail_skew = ((min1_std2neg_skew > self.run[task].min1_skew_resp) & (self.run[task].min1_skew_resp > min1_std2pos_skew)).sum()
                            count_pass_kurt = ((min1_std2neg_kurt < self.run[task].min1_kurt_resp) & (self.run[task].min1_kurt_resp < min1_std2pos_kurt)).sum()
                            count_fail_kurt = ((min1_std2neg_kurt > self.run[task].min1_kurt_resp) & (self.run[task].min1_kurt_resp > min1_std2pos_kurt)).sum()
                            total_skew = len(self.run[task].min1_skew_resp); total_kurt = len(self.run[task].min1_kurt_resp)
                            self.run[task].resp_skew_perc = np.round((count_pass_skew/total_skew)*100,1)
                            self.run[task].resp_skew_perc_above = np.round((count_fail_skew/total_skew)*100,1)
                            self.run[task].resp_kurt_perc = np.round((count_pass_kurt/total_kurt)*100,1)
                            self.run[task].resp_kurt_perc_above = np.round((count_fail_kurt/total_kurt)*100,1)

                            std2neg = np.mean(self.run[task].resp_bpm) - 2 * np.std(self.run[task].resp_bpm)
                            std2pos = np.mean(self.run[task].resp_bpm) + 2 * np.std(self.run[task].resp_bpm)
                            count_pass = ((std2neg < self.run[task].resp_bpm) & (self.run[task].resp_bpm < std2pos)).sum()
                            count_fail = ((std2neg > self.run[task].resp_bpm) & (self.run[task].resp_bpm > std2pos)).sum()
                            total = len(self.run[task].resp_bpm)
                            self.run[task].resp_perc = np.round((count_pass/total)*100,1)
                            self.run[task].resp_perc_above = np.round((count_fail/total)*100,1)

                            ##### Percentage of Resp Rate between 18 and 30
                            #print(self.run[task].pulse_bpm)
                            green_range = filter(lambda x: x>15 and x<40,self.run[task].resp_bpm)
                            self.run[task].resp_perc_green = np.round((len(green_range)/total)*100,1)
                            self.run[task].rr_std = np.round(np.nanstd(self.run[task].pulse_bpm),1)
                            self.run[task].rr_cv = np.round((self.run[task].rr_std/self.run[task].rr),1)
                            # print('total: ',total)
                            # print('len: ',len(green_range))
                            # print('perc: ',self.run[task].resp_perc_green)
                            # print('std: ',self.run[task].rr_std)

                            n_samples = 18
                            self.run[task].resp_blocks = list(divide_chunks(self.run[task].resp_bpm, n_samples))


                    except IOError:
                        print('Error processing {}, {}'.format(self.subid, task))
                        f = open(error_folder + '/error_log.txt', 'a')
                        f.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'proc-biopac-coins', self.subid, 'processing error'))
                        f.close()
                    except ValueError:
                        print('Error processing {}, {}'.format(self.subid, task))
                        f = open(error_folder + '/error_log.txt', 'a')
                        f.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'proc-biopac-coins', self.subid, 'processing error - channel missing data'))
                        f.close()
            self.hasloaded = True
        else:
            print('There is no json file for this subject') 
            f = open(error_folder + '/error_log.txt', 'a')
            f.write('{} : {} : {} : {}\n'.format(datetime.datetime.now(), 'proc-biopac-coins', self.subid, 'no json file'))
            f.close()

def lfr(X, order = 3, cutoff_freq = 0.01):
    #Identify low frequency drift and remove 
    B, A = signal.butter(order, cutoff_freq, output='ba') 
    # get the low-freq component
    tempf = signal.filtfilt(B,A, X)
    #remove it from the raw data
    Xnew = X - tempf
    return(Xnew, tempf)

def round_int(x):
    if x == float("inf") or x == float("-inf"):
        return float('nan') # or x or return whatever makes sense
    return int(round(x))

def plot_subject_struct(physio_data, output_dir='~/'):
    if (os.path.exists(output_dir) is False):
        print('Creating: %s'%output_dir)
        os.makedirs(output_dir)
    fig = plt.figure(num=None, figsize=(20, 12), dpi=72, facecolor='w', edgecolor='k')
    fig.suptitle(physio_data.subid, fontsize=16)
    gs = gridspec.GridSpec(4, 2)
    tasklist = physio_data.tasklist
    for k in range(4):
        ax = fig.add_subplot(gs[k,0])
        rate = physio_data.run[tasklist[k]].hr
        if rate is not np.nan:
            try:
                dat = physio_data.run[tasklist[k]].pulse
                ticdat = np.zeros(len(dat))
                #dat = dat[0:500]
                dat = dat - dat.mean()
                idx = physio_data.run[tasklist[k]].hr_idx
                ticdat[idx] = dat.max()
                #ticdat = ticdat[0:500]
                ax.plot(dat)
                ax.plot(ticdat,'r-')
                ax.set_title(tasklist[k]+", Pulse="+str(rate))
            except IndexError:
                ax.set_title(tasklist[k]+", Pulse=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[k]+", Pulse=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
            
        ax = fig.add_subplot(gs[k,1])
        rate = physio_data.run[tasklist[k]].rr
        if rate is not np.nan:
            dat = physio_data.run[tasklist[k]].resp
            ticdat = np.zeros(len(dat))
            dat = dat[0:500]
            dat = dat - dat.mean()
            idx = physio_data.run[tasklist[k]].rr_idx
            ticdat[idx] = dat.max()
            ticdat = ticdat[0:500]
            ax.plot(dat)
            ax.plot(ticdat,'r-')
            ax.set_title(tasklist[k]+", Resp= "+str(rate))
        else:
            ax.set_title(tasklist[k]+", Resp= Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
    gs.update(wspace=0.1, hspace=0.4)
    figname1 = "teste/"+ physio_data.subid + "_physio_500.png"
    #outfile = os.path.join(output_dir,figname)
    fig.savefig(figname1,transparent=True)

def stability(physio_data, output_dir='~/'):
    blocks = physio_data.run["rest1"].pulse_blocks
    #rate = physio_data.run["rest1"].hr
    fig = plt.figure(num=None, figsize=(6, 3), dpi=100, facecolor='w', edgecolor='k')
    #fig.suptitle(physio_data.subid, fontsize=16)
    sns.set_style("whitegrid")
    ax = fig.add_subplot(111)
    #gs = gridspec.GridSpec(1, 1)
    #ax = fig.add_subplot(111)
    if blocks is not np.nan:
        # try:
        pulse_perc_green = []
        for i in range(len(blocks)):
            if len(blocks[i]) > 9:
                green_range = filter(lambda x: x>60 and x<130, blocks[i])
                pulse_perc_green.append(np.round((len(green_range)/len(blocks[i]))*100,1))
        print(pulse_perc_green)
        ax.plot(range(len(pulse_perc_green)),np.array(pulse_perc_green),marker='o',color='green')
        ax.set_title(physio_data.subid)
        ax.set_ylabel('HR%')
        ax.set_xticks([])
        ax.set_xlabel(physio_data.subid)
        fig.tight_layout()
        figname1 = "teste/"+ physio_data.subid + "_stability.png"
        fig.savefig(figname1,transparent=True)

def plot_subject_struct2(physio_data, output_dir='~/'):
    fig = plt.figure(num=None, figsize=(17, 22), dpi=130, facecolor='w', edgecolor='k')
    fig.suptitle(physio_data.subid, fontsize=16)
    gs = gridspec.GridSpec(16, 3)
    tasklist = physio_data.tasklist
    sns.set_style("white")
    count = 0
    for k in range(4):  
        ax = fig.add_subplot(gs[count,:])
        rate = physio_data.run[tasklist[k]].hr
        if rate is not np.nan:
            try:
                dat = physio_data.run[tasklist[k]].pulse
                #ax.set_xlabel('BPM')
                dat = dat - dat.mean()
                
                ax.set_title(tasklist[k]+", Pulse="+str(rate))
                timex=np.linspace(0,len(dat)/50,num=len(dat))
                time_min = min(timex)
                time_max = max(timex)
                ax.plot(timex/60,dat,linewidth=0.3)
                ax.set_xlim(time_min/60,time_max/60)
                plt.xlabel("Time(m)")
                #print(np.arange(len(dat))/50)
            except:
                ax.set_title(tasklist[k]+", Pulse=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[k]+", Pulse=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        count = count + 1
        ax = fig.add_subplot(gs[count,0])
        ax2 = fig.add_subplot(gs[count,1],sharey=ax)
        ax3 = fig.add_subplot(gs[count,2],sharey=ax)
        #rate = physio_data.run[tasklist[k]].hr
        if rate is not np.nan:
            try:
                dat = physio_data.run[tasklist[k]].pulse
                #ax.set_xlabel('BPM')
                dat = dat - dat.mean()
                #ax.set_title(tasklist[k]+", Pulse="+str(rate))
                timex=np.linspace(0,len(dat)/50,num=len(dat))
                ax.plot(timex/60,dat,linewidth=0.3)
                ax2.plot(timex/60,dat,linewidth=0.3)
                ax3.plot(timex/60,dat,linewidth=0.3)
                if (tasklist[k] == "rest1"):
                    ax.set_xlim(0,0.5);ax2.set_xlim(3,3.5);ax3.set_xlim(5.5,time_max/60)
                else:
                    ax.set_xlim(0,0.5);ax2.set_xlim(2,2.5);ax3.set_xlim(3.5,4)
                ax.set_xlabel("Time(m)");ax2.set_xlabel("Time(m)");ax3.set_xlabel("Time(m)")
                # hide the spines between ax and ax2
                plt.setp(ax2.get_yticklabels(), visible=False)
                plt.setp(ax3.get_yticklabels(), visible=False)
            except:
                #ax.set_title(tasklist[k]+", Pulse=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[k]+", Pulse=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        count = count + 1

    for j in range(4):
        ax = fig.add_subplot(gs[count,:])
        rate = physio_data.run[tasklist[j]].rr
        if rate is not np.nan:
            try:
                dat = physio_data.run[tasklist[j]].resp
                #ax.set_xlabel('BPM')
                dat = dat - dat.mean()
                ax.set_title(tasklist[j]+", Resp="+str(rate))
                timex=np.linspace(0,len(dat)/50,num=len(dat))
                time_min = min(timex)
                time_max = max(timex)
                ax.plot(timex/60,dat,linewidth=0.3)
                ax.set_xlim(time_min/60,time_max/60)
                plt.xlabel("Time(m)")
                #print(np.arange(len(dat))/50)
            except:
                ax.set_title(tasklist[j]+", Resp=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[j]+", Resp=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        count = count + 1
        ax = fig.add_subplot(gs[count,0])
        ax2 = fig.add_subplot(gs[count,1],sharey=ax)
        ax3 = fig.add_subplot(gs[count,2],sharey=ax)
        #rate = physio_data.run[tasklist[j]].rr
        if rate is not np.nan:
            try:
                dat = physio_data.run[tasklist[j]].resp
                #ax.set_xlabel('BPM')
                dat = dat - dat.mean()
                #ax.set_title(tasklist[k]+", Pulse="+str(rate))
                timex=np.linspace(0,len(dat)/50,num=len(dat))
                time_max = max(timex)
                ax.plot(timex/60,dat,linewidth=0.3)
                ax2.plot(timex/60,dat,linewidth=0.3)
                ax3.plot(timex/60,dat,linewidth=0.3)
                #print(tasklist[j])
                if (tasklist[j] == "rest1"):
                    ax.set_xlim(0,0.5);ax2.set_xlim(3,3.5);ax3.set_xlim(5.5,time_max/60)
                else:
                    ax.set_xlim(0,0.5);ax2.set_xlim(2,2.5);ax3.set_xlim(3.5,4)
                ax.set_xlabel("Time(m)");ax2.set_xlabel("Time(m)");ax3.set_xlabel("Time(m)")
                # hide the spines between ax and ax2
                plt.setp(ax2.get_yticklabels(), visible=False)
                plt.setp(ax3.get_yticklabels(), visible=False)
            except:
                #ax.set_title(tasklist[k]+", Pulse=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[j]+", Pulse=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        count = count + 1
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.9, wspace = 0.2, hspace = 0.2)
    #gs.update(wspace=0.1, hspace=0.9)
    fig.tight_layout()
    figname = physio_data.subid + "_physio.png"
    #outfile = os.path.join(output_dir,figname)
    fig.savefig(figname,transparent=True,bbox_inches='tight')


def plot_subject_hr(physio_data, output_dir='~/'):
    rate = physio_data.run["rest1"].hr
    fig,axs = plt.subplots(3, figsize=(10,6))
    if rate is not np.nan:
        df = pd.read_csv('manual_label.csv').dropna()
        dat = physio_data.run["rest1"].pulse
        dat_bpm = np.array(physio_data.run["rest1"].pulse_bpm)
        ticdat = np.zeros(len(dat))
        idx = physio_data.run["rest1"].hr_idx
        cnt=0
        dat = dat - dat.mean()
        while (cnt < (len(idx)-1)):
            ticdat[idx[cnt]:idx[cnt+1]] = dat_bpm[cnt]
            cnt += 1
        kurt = np.round(kurtosis(dat),3)
        skew = np.round(skewness(dat),3)
        pulse_perc_green = physio_data.run["rest1"].pulse_perc_green
        std = physio_data.run["rest1"].hr_std
        cv = physio_data.run["rest1"].hr_cv

        if df['subid'].str.contains(physio_data.subid).any():
            label = df.loc[df['subid'] == physio_data.subid, 'Rating'].iloc[0]
            if label == 1:
                plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+", Skew="+str(skew)+
                        "\nCV="+str(cv)+", Std="+str(std)+", HR%="+str(pulse_perc_green)+", Label: Pass")
            else:
                plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+", Skew="+str(skew)+
                        "\nCV="+str(cv)+", Std="+str(std)+", HR%="+str(pulse_perc_green)+", Label: Fail")
        else:
            plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+"\nSkew="+str(skew)+", CV="+str(cv)+", Std="+
                    str(std)+", HR%="+str(pulse_perc_green))

        timex=np.linspace(0,len(dat)/50,num=len(dat))
        axs[0].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[0].set_xlim(0,2)
        if min(abs(np.array(dat))) > 0.5 or max(abs(np.array(dat))) > 0.5:
            axs[0].set_ylim(-0.5, 0.5)
        axs1 = axs[0].twinx()
        axs1.plot(timex/60,ticdat,'r-',linewidth=0.5,label="Heart Rate (BPM)")
        axs1.tick_params(axis='y', labelcolor='tab:red')
        axs1.yaxis.set_major_locator(plt.MaxNLocator(5))
        axs1.set_ylim([0,200])

        # # added these three lines
        # lns = line_plot1+line_plot2
        # labs = [l.get_label() for l in lns]
        axs1.legend()

        axs[1].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[1].set_xlim(2,4)
        if min(abs(np.array(dat))) > 0.5 or max(abs(np.array(dat))) > 0.5:
            axs[1].set_ylim(-0.5, 0.5)
        axs2 = axs[1].twinx()
        axs2.plot(timex/60,ticdat,'r-',linewidth=0.5,label="Heart Rate (BPM)")
        axs2.tick_params(axis='y', labelcolor='tab:red')
        axs2.yaxis.set_major_locator(plt.MaxNLocator(5))
        axs2.set_ylim([0,200])

        axs[2].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[2].set_xlim(4,6)
        if min(abs(np.array(dat))) > 0.5 or max(abs(np.array(dat))) > 0.5:
           axs[2].set_ylim(-0.5, 0.5)
        axs3 = axs[2].twinx()
        axs3.plot(timex/60,ticdat,'r-',linewidth=0.5,label="Heart Rate (BPM)")
        axs3.tick_params(axis='y', labelcolor='tab:red')
        axs3.yaxis.set_major_locator(plt.MaxNLocator(5))
        axs3.set_ylim([0,200])

        axs[2].set_xlabel("Time (minutes)", fontsize=12)
        plt.xlabel("Time (minutes)", fontsize=12)

        fig.tight_layout()
        fig.subplots_adjust(top=0.90)
        figname = "teste/rest1/"+ physio_data.subid + "_rest1_physio.png"
        fig.savefig(figname,transparent=True,bbox_inches='tight')

def plot_subject_hr_peaks(physio_data, output_dir='~/'):
    rate = physio_data.run["rest1"].hr
    fig,axs = plt.subplots(3, figsize=(10,6))
    if rate is not np.nan:
        df = pd.read_csv('manual_label.csv').dropna(subset=['Rating'])
        dat = physio_data.run["rest1"].pulse
        dat_bpm = physio_data.run["rest1"].pulse_bpm
        dat = dat - dat.mean()
        ticdat = np.zeros(len(dat))
        ticdat[ ticdat==0 ] = np.nan
        idx = physio_data.run["rest1"].hr_idx
        ticdat[idx] = dat[idx]

        kurt = np.round(kurtosis(dat_bpm, nan_policy="omit"),3)
        skew = np.round(skewness(dat_bpm, nan_policy="omit"),3)
        pulse_perc_green = physio_data.run["rest1"].pulse_perc_green
        std = physio_data.run["rest1"].hr_std
        cv = physio_data.run["rest1"].hr_cv

        if df['subid'].str.contains(physio_data.subid).any():
            label = df.loc[df['subid'] == physio_data.subid, 'Rating'].iloc[0]
            if label == 1:
                plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+", Skew="+str(skew)+
                        "\nCV="+str(cv)+", Std="+str(std)+", HR%="+str(pulse_perc_green)+", Label: Pass")
            else:
                plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+", Skew="+str(skew)+
                        "\nCV="+str(cv)+", Std="+str(std)+", HR%="+str(pulse_perc_green)+", Label: Fail")
        else:
            plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+"\nSkew="+str(skew)+", CV="+str(cv)+", Std="+
                    str(std)+", HR%="+str(pulse_perc_green))

        timex=np.linspace(0,len(dat)/50,num=len(dat))
        axs[0].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[0].plot(timex/60,ticdat,'r.',markersize=2,label="Heart Rate (BPM)")
        axs[0].set_xlim(0,2)
        
        if min(abs(np.array(dat))) > 0.5 or max(abs(np.array(dat))) > 0.5:
            axs[0].set_ylim(-0.5, 0.5)


        axs[1].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[1].plot(timex/60,ticdat,'r.',markersize=2,label="Heart Rate (BPM)")
        axs[1].set_xlim(2,4)
        if min(abs(np.array(dat))) > 0.5 or max(abs(np.array(dat))) > 0.5:
            axs[1].set_ylim(-0.5, 0.5)
        

        axs[2].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[2].plot(timex/60,ticdat,'r.',markersize=2,label="Heart Rate (BPM)")
        axs[2].set_xlim(4,6)
        if min(abs(np.array(dat))) > 0.5 or max(abs(np.array(dat))) > 0.5:
           axs[2].set_ylim(-0.5, 0.5)
        

        axs[2].set_xlabel("Time (minutes)", fontsize=12)
        plt.xlabel("Time (minutes)", fontsize=12)

        fig.tight_layout()
        fig.subplots_adjust(top=0.90)
        figname = "teste/rest1/hr/"+ physio_data.subid + "_rest1_physio_hr.png"
        fig.savefig(figname,bbox_inches='tight')

def plot_subject_rr_peaks(physio_data, output_dir='~/'):
    rate = physio_data.run["rest1"].rr
    fig,axs = plt.subplots(3, figsize=(10,6))
    if rate is not np.nan:
        # df = pd.read_csv('manual_label.csv').dropna()
        dat = physio_data.run["rest1"].resp
        dat_bpm = physio_data.run["rest1"].resp_bpm
        dat = dat - dat.mean()
        ticdat = np.zeros(len(dat))
        ticdat[ ticdat==0 ] = np.nan
        idx = physio_data.run["rest1"].rr_idx
        ticdat[idx] = dat[idx]

        kurt = np.round(kurtosis(dat_bpm, nan_policy="omit"),3)
        skew = np.round(skewness(dat_bpm, nan_policy="omit"),3)
        resp_perc_green = physio_data.run["rest1"].resp_perc_green
        std = physio_data.run["rest1"].rr_std
        cv = physio_data.run["rest1"].rr_cv

        # if df['subid'].str.contains(physio_data.subid).any():
        #     label = df.loc[df['subid'] == physio_data.subid, 'Rating'].iloc[0]
        #     if label == 1:
        #         plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+", Skew="+str(skew)+
        #                 "\nCV="+str(cv)+", Std="+str(std)+", RR%="+str(resp_perc_green)+", Label: Pass")
        #     else:
        #         plt.suptitle(physio_data.subid+", rest1, Pulse="+str(rate)+", Kurt="+str(kurt)+", Skew="+str(skew)+
        #                 "\nCV="+str(cv)+", Std="+str(std)+", RR%="+str(resp_perc_green)+", Label: Fail")
        # else:
        plt.suptitle(physio_data.subid+", rest1, Resp="+str(rate)+", Kurt="+str(kurt)+"\nSkew="+str(skew)+", CV="+str(cv)+", Std="+
                str(std)+", RR%="+str(resp_perc_green))

        timex=np.linspace(0,len(dat)/50,num=len(dat))
        axs[0].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[0].plot(timex/60,ticdat,'r.',markersize=2,label="Heart Rate (BPM)")
        axs[0].set_xlim(0,2)

        axs[1].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[1].plot(timex/60,ticdat,'r.',markersize=2,label="Heart Rate (BPM)")
        axs[1].set_xlim(2,4)
        

        axs[2].plot(timex/60,np.array(dat),linewidth=0.3,label="ECG")
        axs[2].plot(timex/60,ticdat,'r.',markersize=2,label="Heart Rate (BPM)")
        axs[2].set_xlim(4,6)
        
        axs[2].set_xlabel("Time (minutes)", fontsize=12)
        plt.xlabel("Time (minutes)", fontsize=12)

        fig.tight_layout()
        fig.subplots_adjust(top=0.90)
        figname = "teste/rest1/rr/"+ physio_data.subid + "_rest1_physio_rr.png"
        fig.savefig(figname,bbox_inches='tight')

def pulse_boxplot(physio_data, output_dir='~/'):
    sns.set_style("whitegrid")
    fig = plt.figure(num=None, figsize=(12, 24), dpi=130, facecolor='w', edgecolor='k')
    fig.suptitle(physio_data.subid, fontsize=16)
    gs = gridspec.GridSpec(4, 2)
    tasklist = physio_data.tasklist
    for k in range(4):
        rate = physio_data.run[tasklist[k]].hr
        ax = fig.add_subplot(gs[k,0])
        if rate is not np.nan:
            try:
                dat = np.array(physio_data.run[tasklist[k]].pulse_bpm)
                # std2neg = dat.mean() - 2 * dat.std()
                # std2pos = dat.mean() + 2 * dat.std()
                # count_pass = ((std2neg < dat) & (dat < std2pos)).sum()
                # total = len(dat)
                # perc = np.round((count_pass/total)*100,1)
                #print(perc)
                #print("perc: %8.2f", perc)
                #kurt = physio_data.run[tasklist[k]].pulse_kurt
                #skew = physio_data.run[tasklist[k]].pulse_skew
                ax.set_ylabel('BPM')
                ax.set_title(tasklist[k]+", Pulse="+str(rate))
                ax.boxplot(dat[~np.isnan(dat)], notch=1)
            except:
                ax.set_title(tasklist[k]+", Pulse=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[k]+", Pulse=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        rate = physio_data.run[tasklist[k]].hr
        ax = fig.add_subplot(gs[k,1])
        if rate is not np.nan:
            dat = np.array(physio_data.run[tasklist[k]].pulse_bpm)
            #print('Pass: ', count_pass)
            #kurt = physio_data.run[tasklist[k]].pulse_kurt
            #skew = physio_data.run[tasklist[k]].pulse_skew
            kurt = np.round(kurtosis(dat),3)
            skew = np.round(skewness(dat),3)
            ax.hist(dat[~np.isnan(dat)], bins=60) 
            ax.set_xlabel('BPM')
            ax.set_ylabel('Frequency')
            ax.set_title(tasklist[k]+", Pulse="+str(rate)+", Skew="+str(skew)+", Kurt="+str(kurt))
        else:
            ax.set_title(tasklist[k]+", Pulse= Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
    gs.update(wspace=0.2, hspace=0.4)
    #fig.tight_layout()
    figname1 = physio_data.subid + "_pulse_boxplot.png"
    fig.savefig(figname1,transparent=True)

def resp_boxplot(physio_data, output_dir='~/'):
    sns.set_style("whitegrid")
    fig = plt.figure(num=None, figsize=(12, 24), dpi=130, facecolor='w', edgecolor='k')
    fig.suptitle(physio_data.subid, fontsize=16)
    gs = gridspec.GridSpec(4, 2)
    tasklist = physio_data.tasklist
    for k in range(4):
        rate = physio_data.run[tasklist[k]].rr
        ax = fig.add_subplot(gs[k,0])
        if rate is not np.nan:
            try:
                dat = np.array(physio_data.run[tasklist[k]].resp_bpm)
                # std2neg = dat.mean() - 2 * dat.std()
                # std2pos = dat.mean() + 2 * dat.std()
                # count_pass = ((std2neg < dat) & (dat < std2pos)).sum()
                # total = len(dat)
                # perc = np.round((count_pass/total)*100,1)
                #print(perc)
                #kurt = physio_data.run[tasklist[k]].resp_kurt
                #skew = physio_data.run[tasklist[k]].resp_skew
                ax.set_ylabel('BPM')
                ax.set_title(tasklist[k]+", Resp="+str(rate))
                ax.boxplot(dat[~np.isnan(dat)], notch=1)
            except:
                ax.set_title(tasklist[k]+", Pulse=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[k]+", Resp=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        rate = physio_data.run[tasklist[k]].rr
        ax = fig.add_subplot(gs[k,1])
        if rate is not np.nan:
            dat = np.array(physio_data.run[tasklist[k]].resp_bpm)
            #kurt = physio_data.run[tasklist[k]].resp_kurt
            #skew = physio_data.run[tasklist[k]].resp_skew
            kurt = np.round(kurtosis(dat),3)
            skew = np.round(skewness(dat),3)
            ax.hist(dat[~np.isnan(dat)], bins=60) 
            ax.set_xlabel('BPM')
            ax.set_ylabel('Frequency')
            ax.set_title(tasklist[k]+", Resp="+str(rate)+", Skew="+str(skew)+", Kurt="+str(kurt))
        else:
            ax.set_title(tasklist[k]+", Pulse= Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
    gs.update(wspace=0.2, hspace=0.4)
    #fig.tight_layout()
    figname1 = physio_data.subid + "_resp_boxplot.png"
    fig.savefig(figname1,transparent=True)

def boxplot_1min(physio_data, output_dir='~/'):
    if physio_data.run["rest1"].min1_pulse is not np.nan:
        sns.set_style("whitegrid")
        fig = plt.figure(num=None, figsize=(24, 7), dpi=130, facecolor='w', edgecolor='k')
        #fig.suptitle(physio_data.subid, fontsize=16)
        gs = gridspec.GridSpec(2, 6)
        
        for k in range(6):
            rate = physio_data.run["rest1"].hr
            ax = fig.add_subplot(gs[0,k])
            if rate is not np.nan:
                try:
                    dat = np.array(physio_data.run["rest1"].min1_pulse[k])
                    kurt = physio_data.run["rest1"].min1_kurt_pulse[k]
                    skew = physio_data.run["rest1"].min1_skew_pulse[k]
                    ax.set_xlabel('BPM')
                    ax.set_ylabel('Frequency')
                    ax.set_title("rest1, Pulse="+str(rate)+", Skew="+str(skew)+", Kurt="+str(kurt))
                    ax.hist(dat[~np.isnan(dat)], bins=60) 
                except:
                    ax.set_title("rest1, Pulse=Unknown")
                    ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
            else:
                ax.set_title("rest1, Pulse=Unknown")
                ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
            rate = physio_data.run["rest1"].rr
            ax = fig.add_subplot(gs[1,k])
            if rate is not np.nan:
                    dat = np.array(physio_data.run["rest1"].min1_resp[k])
                    kurt = physio_data.run["rest1"].min1_kurt_resp[k]
                    skew = physio_data.run["rest1"].min1_skew_resp[k]
                    ax.set_xlabel('BPM')
                    ax.set_ylabel('Frequency')
                    ax.set_title("rest1, Resp="+str(rate)+", Skew="+str(skew)+", Kurt="+str(kurt))
                    ax.hist(dat[~np.isnan(dat)], bins=60)
            else:
                ax.set_title("rest1, Pulse= Unknown")
                ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        #gs.update(wspace=0.6, hspace=0.3)
        fig.tight_layout()
        figname1 = "teste/"+ physio_data.subid + "_1min_hist.png"
        fig.savefig(figname1,transparent=True)

def heart_resp_all(physio_data, output_dir='~/'):
    sns.set_style("whitegrid")
    fig = plt.figure(num=None, figsize=(12, 24), dpi=72, facecolor='w', edgecolor='k')
    fig.suptitle(physio_data.subid, fontsize=16)
    gs = gridspec.GridSpec(4, 1)
    tasklist = physio_data.tasklist
    for k in range(4):
        ax = fig.add_subplot(gs[k,0])
        rate = physio_data.run[tasklist[k]].hr
        if rate is not np.nan:
            try:
                dat = physio_data.run[tasklist[k]].pulse
                ticdat = np.zeros(len(dat))
                #print ticdat
                dat = dat[0:3000]
                dat = dat - dat.mean()
                #ax.set_xlabel('BPM')
                ax.set_title(tasklist[k]+", Pulse="+str(rate))
                idx = physio_data.run[tasklist[k]].hr_idx
                ticdat[idx] = dat.max()
                #ax.plot(ticdat,'r-')
                ax.plot(dat)
            except:
                ax.set_title(tasklist[k]+", Pulse=Unknown")
                ax.text(0.25,0.4, "ERROR OCCURRED DURING PROCESSING")
        else:
            ax.set_title(tasklist[k]+", Pulse=Unknown")
            ax.text(0.25,0.4, "FILE NOT FOUND,\nOR PROCESSED WITH ERROR")
        
    gs.update(wspace=0.1, hspace=0.4)
    #figname = physio_data['subject_id'] + "_physio.png"
    #outfile = os.path.join(output_dir,figname)
    #fig.savefig(outfile)
    
    #sns_plot = sns.swarmplot(data=dat)
    #fig.tight_layout()
    figname1 = physio_data.subid + "_all_hr.png"
    #outfile1 = os.path.join(output_dir,figname1)
    fig.savefig(figname1,transparent=True)
    #print(outfile1)
    #fig.savefig(figname1)

def save_physio_csv(physio_data, output_dir):
    output_csv = os.path.join(output_dir, 'physio_values_new3.csv')
    odat = {}
    odat["subject_id"] = physio_data.subid
    for task in physio_data.tasklist:
        odat[task+'_hr'] = physio_data.run[task].hr
        odat[task+'_kurt_hr'] = physio_data.run[task].pulse_kurt
        odat[task+'_kurt_perc_hr'] = physio_data.run[task].pulse_kurt_perc
        odat[task+'_kurt_perc_above_hr'] = physio_data.run[task].pulse_kurt_perc_above
        odat[task+'_skew_hr'] = physio_data.run[task].pulse_skew
        odat[task+'_skew_perc_hr'] = physio_data.run[task].pulse_skew_perc
        odat[task+'_skew_perc_above_hr'] = physio_data.run[task].pulse_skew_perc_above
        odat[task+'_perc_hr'] = physio_data.run[task].pulse_perc
        odat[task+'_perc_above_hr'] = physio_data.run[task].pulse_perc_above

        odat[task+'_rr'] = physio_data.run[task].rr
        odat[task+'_kurt_rr'] = physio_data.run[task].resp_kurt
        odat[task+'_kurt_perc_rr'] = physio_data.run[task].resp_kurt_perc
        odat[task+'_kurt_perc_above_rr'] = physio_data.run[task].resp_kurt_perc_above
        odat[task+'_skew_rr'] = physio_data.run[task].resp_skew
        odat[task+'_skew_perc_rr'] = physio_data.run[task].resp_skew_perc
        odat[task+'_skew_perc_above_rr'] = physio_data.run[task].resp_skew_perc_above
        odat[task+'_perc_rr'] = physio_data.run[task].resp_perc
        odat[task+'_perc_above_rr'] = physio_data.run[task].resp_perc_above
    df = pd.DataFrame([odat])
    if os.path.isfile(output_csv) is True:
        indf = pd.read_csv(output_csv)
        df = df.append(indf)
    print('Writing hr/rr to: %s'%output_csv)
    #df.to_csv(output_csv, index=False)

def save_physio_csv_rest1_rr(physio_data, output_dir):
    output_csv = os.path.join(output_dir, 'physio_values_rest1_rr2.csv')
    odat = {}
    odat["subject_id"] = physio_data.subid
    for task in physio_data.tasklist:
        if "rest1" in task:
            odat[task+'_rr'] = physio_data.run[task].rr
            odat[task+'_std_rr'] = physio_data.run[task].rr_std
            odat[task+'_cv_rr'] = physio_data.run[task].rr_cv
            odat[task+'_kurt_rr'] = physio_data.run[task].resp_kurt
            odat[task+'_skew_rr'] = physio_data.run[task].resp_skew
            odat[task+'_perc_green_rr'] = physio_data.run[task].resp_perc_green
            #odat[task+'_perc_green_rr'] = physio_data.run[task].resp_perc_green

    df = pd.DataFrame([odat])
    if os.path.isfile(output_csv) is True:
        indf = pd.read_csv(output_csv)
        df = df.append(indf)
    print('Writing hr/rr to: %s'%output_csv)
    df.to_csv(output_csv, index=False)

def save_physio_csv_rest1_hr(physio_data, output_dir):
    output_csv = os.path.join(output_dir, 'physio_values_rest1_hr2.csv')
    odat = {}
    odat["subject_id"] = physio_data.subid
    for task in physio_data.tasklist:
        if "rest1" in task:
            odat[task+'_hr'] = physio_data.run[task].hr
            odat[task+'_std_hr'] = physio_data.run[task].hr_std
            odat[task+'_cv_hr'] = physio_data.run[task].hr_cv
            odat[task+'_kurt_hr'] = physio_data.run[task].pulse_kurt
            odat[task+'_skew_hr'] = physio_data.run[task].pulse_skew
            odat[task+'_perc_green_hr'] = physio_data.run[task].pulse_perc_green
            #odat[task+'_perc_green_rr'] = physio_data.run[task].pulse_perc_green

    df = pd.DataFrame([odat])
    if os.path.isfile(output_csv) is True:
        indf = pd.read_csv(output_csv)
        df = df.append(indf)
    print('Writing hr/rr to: %s'%output_csv)
    df.to_csv(output_csv, index=False)

def save_physio_tsv(physio_data, output_dir):
    tasklist = physio_data.tasklist
    subid = physio_data.subid
    subid2 = physio_data.subid
    tsv_name = {}
    tsv_name['rest1'] = subid+'_task-rest_run-01_physio'
    tsv_name['rest2'] = subid+'_task-rest_run-02_physio'
    tsv_name['face1'] = subid+'_task-faces_run-01_physio'
    tsv_name['face2'] = subid+'_task-faces_run-02_physio'    
    physio_json = '''{
        "SamplingFrequency": 50.0,
        "StartTime": 0.00,
        "Columns": ["cardiac", "respiratory"]
        }'''
    for task in tasklist:
        hr = physio_data.run[task].hr
        rr = physio_data.run[task].rr
        if hr is not np.nan and rr is not np.nan:
            outpath = os.path.join(output_dir, subid2, 'func')
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            outfile = os.path.join(output_dir,subid2,"func",tsv_name[task]+'.tsv')
            print("Writing: %s"%outfile)
            k = []
            k.append(physio_data.run[task].pulse[:])
            k.append(physio_data.run[task].resp[:])
            p = np.array(k)
            #np.savetxt(outfile, p.transpose(), delimiter='\t')
            jsonpath = os.path.join(output_dir, subid2, 'func', tsv_name[task]+'.json')
            jsonfile = open(jsonpath,'w')
            jsonfile.write(physio_json)
            jsonfile.close()
        
