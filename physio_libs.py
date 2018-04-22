#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 10:05:12 2018

@author: stan
"""
import bioread as br
import numpy as np
import scipy.signal as signal
import os.path as path
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

class PhysData():
    def __init__(self):
        self.pulse = np.nan
        self.resp = np.nan
        self.hr = np.nan
        self.rr = np.nan 
        self.hr_idx = np.nan
        self.rr_idx = np.nan
        self.name = ""

class PhysioObject():
    def __init__(self):
        self.subid = ""
        self.tasklist = ['face1', 'face2', 'rest1', 'rest2']
        self.target_sampling_rate = 50
        self.natve_sampling_rate = np.nan
        self.hasloaded = False
        self.run = {}
        for task in self.tasklist:
            self.run[task] = PhysData()

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
            if cname == "TRIGGER" or cname == trigger_str:
                trig = acq.channels[k].data
            elif cname == "PULSE" or cname == pulse_str:
                pulse = acq.channels[k].data
            elif cname == "RESP" or cname == resp_str:
                resp = acq.channels[k].data
        idx = np.where(trig)
        pulse = pulse[idx]
        resp = resp[idx]
        return(pulse, resp)
        
    def load_from_template(self,infile):
        infile = path.abspath(path.expanduser(infile))
        with open(infile) as json_data:
            d = json.load(json_data)
        for task in self.tasklist:
            taskfile = path.abspath(path.expanduser(d[task]))
            if path.isfile(taskfile):
                print("loading: %s"%taskfile)
                data = br.read_file(taskfile)
                pulse, resp = self.get_channels(data)
                self.run[task].resp = resp
                self.run[task].pulse= pulse
                print("Processing: %s, %s"%(self.subid, task))
                self.samples_per_second = int(data.samples_per_second)
                self.run[task].pulse = signal.medfilt(self.run[task].pulse,3)
                self.run[task].resp = signal.medfilt(self.run[task].resp,3) 
                if self.samples_per_second != self.target_sampling_rate:
                    scale = int(self.samples_per_second / self.target_sampling_rate)
                    self.run[task].pulse = signal.decimate(self.run[task].pulse,scale,zero_phase=True)
                    self.run[task].resp = signal.decimate(self.run[task].resp,scale,zero_phase=True)
                self.run[task].hr_idx = signal.find_peaks_cwt(self.run[task].pulse, np.arange(1,35))
                self.run[task].hr = int(len(self.run[task].hr_idx) / ((len(self.run[task].pulse)/self.target_sampling_rate)/60.0))
                self.run[task].rr_idx = signal.find_peaks_cwt(moving_average(self.run[task].resp,50), np.arange(1,70))
                self.run[task].rr = int(len(self.run[task].rr_idx) / ((len(self.run[task].resp)/self.target_sampling_rate)/60.0))
            else:
                print("No acq file found for: %s, %s" % (self.subid, task))                
        self.hasloaded = True

def lfr(X, order = 3, cutoff_freq = 0.01):
    #Identify low frequency drift and remove 
    B, A = signal.butter(order, cutoff_freq, output='ba') 
    # get the low-freq component
    tempf = signal.filtfilt(B,A, X)
    #remove it from the raw data
    Xnew = X - tempf
    return(Xnew, tempf)

def plot_subject_struct(physio_data, output_dir='~/'):
    if (os.path.exists(output_dir) is False):
        print('Creating: %s'%output_dir)
        os.makedirs(output_dir)
    fig = plt.figure(num=None, figsize=(12, 12), dpi=72, facecolor='w', edgecolor='k')
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
                dat = dat[0:500]
                dat = dat - dat.mean()
                idx = physio_data.run[tasklist[k]].hr_idx
                ticdat[idx] = dat.max()
                ticdat = ticdat[0:500]
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
    figname = physio_data.subid + "_physio.png"
    outfile = os.path.join(output_dir,figname)
    fig.savefig(outfile)

def save_physio_csv(physio_data, output_dir):
    output_csv = os.path.join(output_dir, 'physio_values.csv')
    if os.path.isfile(output_csv) is False:
        hdrstr = "subject_id"
        for task in physio_data.tasklist:
            hdrstr = hdrstr+','+task+'_hr,'+task+'_rr'
        csv_out = open(output_csv, 'w')
        csv_out.write(hdrstr+'\n')
        csv_out.close()
    outstr = physio_data.subid
    for task in physio_data.tasklist:
        outstr = outstr+','+str(physio_data.run[task].hr) + ',' + str(physio_data.run[task].rr)
    csv_out = open(output_csv, 'a')
    csv_out.write(outstr+'\n')
    csv_out.close()

def save_physio_tsv(physio_data, output_dir):
    tasklist = physio_data.tasklist
    subid = physio_data.subid
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
            outfile = os.path.join(output_dir,subid,"func",tsv_name[task]+'.tsv')
            print("Writing: %s"%outfile)
            k = []
            k.append(physio_data.run[task].pulse[:])
            k.append(physio_data.run[task].resp[:])
            p = np.array(k)
            np.savetxt(outfile, p.transpose(), delimiter='\t')
            jsonpath = os.path.join(output_dir, tsv_name[task]+'.json')
            jsonfile = open(jsonpath,'w')
            jsonfile.write(physio_json)
            jsonfile.close()
        