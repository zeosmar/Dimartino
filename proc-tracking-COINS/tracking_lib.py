#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 12:28:38 2018

@author: jcloud
"""
# In[Info]

"""

-how to import information about screen resolution? any way of acquiring that?

"""
# In[Import]:

import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate, signal
import pandas as pd
import datetime
import json

# In[TrackData]:

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def flipx(data):
    gazex = data.gazex[:]
    
    c = data.res[0] / 2
    
    for i in range(gazex.size):
        x = c - gazex[i]
        gazex[i] = c + x
        
    data.gazex = gazex
    
    return data
    
def flipy(data):
    gazey = data.gazey[:]
    
    c = data.res[1] / 2
    
    for i in range(gazey.size):
        x = c - gazey[i]
        gazey[i] = c + x
        
    data.gazey = gazey
        
    return data

def flipyother(l, c):
    gazey = l[:]
    
    for i in range(len(gazey)):
        x = c - gazey[i]
        gazey[i] = c + x
        
    return gazey

def dilationspeed(data):
    
    pupil = np.array(data.pupil[:])
    gazex = np.array(data.gazex[:])
    gazey = np.array(data.gazey[:])
    time = np.array(data.time[:])
    
    data.startsize = pupil.size
    
    dilation_speed = []
    for i in range(pupil.size):
        try:
            x = max(abs(float(pupil[i] - pupil[i-1])/float(time[i] - time[i-1])),
                    abs(float(pupil[i+1] - pupil[i])/float(time[i+1]-time[i])))
            dilation_speed.append(x)
        except:
            dilation_speed.append(0.0)
            
    med = np.median(dilation_speed)
    
    madlist = []
    for i in range(pupil.size):
        madlist.append(abs(dilation_speed[i] - med))
    
    mad = np.median(madlist)
    
    thresh = med + (2 * mad)
    
    dilation_speed = np.array(dilation_speed)
    
    cut = dilation_speed < thresh
    gazex = gazex[cut]
    gazey = gazey[cut]
    pupil = pupil[cut]
    time = time[cut]
    
    data.gazex = gazex[:]
    data.gazey = gazey[:]
    data.pupil = pupil[:]
    data.time = time[:]
    
    data = interp(data)
    
    return data

def interp(data):
    
    gazex = np.array(data.gazex[:])
    gazey = np.array(data.gazey[:])
    pupil = np.array(data.pupil[:])
    time = np.array(data.time[:])
    
    if time[0] != data.org_start:

        gx = [data.org_first[0]]
        gy = [data.org_first[1]]
        p = [data.org_first[2]]
        t = [data.org_start]

        gx.extend(list(gazex))
        gy.extend(list(gazey))
        p.extend(list(pupil))
        t.extend(list(time))

        gazex = gx
        gazey = gy
        pupil = p
        time = t
        
    else:

        gazex = list(gazex)
        gazey = list(gazey)
        pupil = list(pupil)
        time = list(time)
    
    if time[-1] != data.org_end:
        gazex.append(data.org_last[0])
        gazey.append(data.org_last[1])
        pupil.append(data.org_last[2])
        time.append(data.org_end)
        
    gazex = np.array(gazex)
    gazey = np.array(gazey)
    pupil = np.array(pupil)
    time = np.array(time)
    
    interfunc = interpolate.interp1d(time, pupil)
    interfunc2 = interpolate.interp1d(time, gazex)
    interfunc3 = interpolate.interp1d(time, gazey)
    
    time = np.arange(data.org_start, data.org_end + (1000./data.sampling_rate), (1000./data.sampling_rate))

    pupil = interfunc(time)
    gazex = interfunc2(time)
    gazey = interfunc3(time)
    
    data.time = time[:]
    data.pupil = pupil[:]
    data.gazex = gazex[:]
    data.gazey = gazey[:]
    
    return data

def invalid(data):
    
    gazex = data.gazex[:]
    gazey = data.gazey[:]
    pupil = data.pupil[:]
    time = data.time[:]
    
    data.org_first = [gazex[0], gazey[0], pupil[0]]
    data.org_last = [gazex.iloc[-1], gazey.iloc[-1], pupil.iloc[-1]]

    cuta = np.logical_and(gazex > 0, gazex < 1920 + 50)
    gazex = gazex[cuta]
    gazey = gazey[cuta]
    pupil = pupil[cuta]
    time = time[cuta]
    
    cutb = np.logical_and(gazey > 0, gazey < 1080 + 50)
    gazex = gazex[cutb]
    gazey = gazey[cutb]
    pupil = pupil[cutb]
    time = time[cutb]
    
    data.endsize = pupil.size
    
    data.gazex = gazex
    data.gazey = gazey
    data.pupil = pupil
    data.time = time
    
    data = interp(data)
    
    return data

def normalize(data):
    
    gazex = data.gazex[:]
    gazey = data.gazey[:]
    pupil = data.pupil[:]
    time = data.time[:]
    
    mean = pupil.mean()
    stddev = pupil.std()
    pupil = (pupil - mean) / stddev
    
    cut = np.logical_and(pupil < 3, pupil > -3)
    gazex = gazex[cut]
    gazey = gazey[cut]
    pupil = pupil[cut]
    time = time[cut]
    
    pupil = signal.detrend(pupil)
    
    data.gazex = gazex
    data.gazey = gazey
    data.pupil = pupil
    data.time = time
    
    data = interp(data)
    
    return data

def trendline(data):
    
    gazex = np.array(data.gazex[:])
    gazey = np.array(data.gazey[:])
    pupil = np.array(data.pupil[:])
    time = np.array(data.time[:])
    
    inter_pupil = pupil[:]
    inter_time = time[:]
    trend_pupil = signal.medfilt(inter_pupil, kernel_size = 501)
    
    med = np.median(trend_pupil)
    
    mad_list = []
    for i in range(trend_pupil.size):
        mad_list.append(abs(trend_pupil[i] - med))
        
    mad = np.median(mad_list)
    
    pos_limit = trend_pupil + mad
    neg_limit = trend_pupil - mad
    
    cuta = pupil > neg_limit
    cutb = pupil < pos_limit
    cutc = np.logical_and(cuta, cutb)
    
    inter_time = inter_time[cutc]
    inter_pupil = inter_pupil[cutc]
    
    if time[-1] not in inter_time:
        inter_time =  np.append(inter_time, np.array(time[-1]))
        inter_pupil =  np.append(inter_pupil, np.array(0))
    if time[0] not in inter_time:
        inter_time =  np.append(inter_time, np.array(time[0]))
        inter_pupil =  np.append(inter_pupil, np.array(0))
        
    inter_func = interpolate.interp1d(inter_time, inter_pupil)
    time = np.arange(data.org_start, data.org_end + (1000/data.sampling_rate), (1000/data.sampling_rate))
    inter_pupil = inter_func(inter_time)
    
    
    trend_pupil = signal.medfilt(inter_pupil, kernel_size=501)
    
    med = np.median(trend_pupil)
    
    mad_list = []
    for i in range(trend_pupil.size):
        mad_list.append(abs(trend_pupil[i] - med))
        
    mad = np.median(mad_list)
    
    inter_func = interpolate.interp1d(inter_time, inter_pupil)
    inter_func2 = interpolate.interp1d(inter_time, trend_pupil)
    inter_time = time
    inter_pupil = inter_func(inter_time)
    trend_pupil = inter_func2(inter_time)
    
    pos_limit = trend_pupil + (.5 * mad)
    neg_limit = trend_pupil - (.5 * mad)
    
    cutd = inter_pupil > neg_limit
    cute = inter_pupil < pos_limit
    cutf = np.logical_and(cutd, cute)
    
    gazex = gazex[cutf]
    gazey = gazey[cutf]
    pupil = pupil[cutf]
    time = time[cutf]
    
    blink_count = 0
    t = 0
    for i in range(pupil.size):
        if time[i] - t >= 300 and time[i] - t <= 1250:
            blink_count += 1
            t = time[i]
        else:
            t = time[i]
    data.blink_count = blink_count
    data.blink_rate = float(blink_count) / float(float(time[-1]) / float(60000))
    
    data.gazex = gazex
    data.gazey = gazey
    data.pupil = pupil
    data.time = time
    
    data = interp(data)
    
    return data

def decimate(array, end_mseconds_p_sample, cur_sampling_rate):
    cur_ms_p_samp = 1000/cur_sampling_rate
    sample_step = int(end_mseconds_p_sample / cur_ms_p_samp)
    return array[::int(sample_step)]

def downsample(data, rate):
    
    gazex = data.gazex[:]
    gazey = data.gazey[:]
    pupil = data.pupil[:]
    time = data.time[:]
    
    gazex = decimate(gazex, rate, data.sampling_rate)
    gazey = decimate(gazey, rate, data.sampling_rate)
    pupil = decimate(pupil, rate, data.sampling_rate)
    time = decimate(time, rate, data.sampling_rate)
    
    data.sampling_rate = 1000. / rate
    
    data.gazex = gazex
    data.gazey = gazey
    data.pupil = pupil
    data.time = time
    data.org_start = time[0]
    data.org_end = time[-1]
    
    return data

def cuttostart():
    pass

class TrackData:
    
    def __init__(self):
        
        self.gazex = np.nan
        self.gazey = np.nan
        self.pupil = np.nan
        self.time = np.nan
        self.sampling_rate = np.nan
        self.org_start = np.nan
        self.org_end = np.nan
        self.org_first = np.nan
        self.org_last = np.nan
        self.startsize = np.nan
        self.endsize = np.nan
        self.blink_count = np.nan
        self.blink_rate = np.nan
        self.res = (1920, 1080)
        self.qc_metrics = []
        self.graphs = ()
        self.name = ''

    
    def qc(self):
        
        res = self.res
        
        l_c = [(res[0] * .3), (res[1] * .65)]
        r_c = [(res[0] * .7), (res[1] * .64)]
        c_c = [(res[0] * .5), (res[1] * .33)]
        
        c = res[1] / 2
        
        l_c[1] = c - l_c[1]
        l_c[1] = c + l_c[1]
        
        r_c[1] = c - r_c[1]
        r_c[1] = c + r_c[1]
        
        c_c[1] = c - c_c[1]
        c_c[1] = c + c_c[1]
        
        x = 195/2
        y = 240/2
        
        #ROI LEFT
        l_x = [l_c[0]+x, l_c[0]+x, l_c[0]-x, l_c[0]-x, l_c[0]+x]
        l_y = [l_c[1]-y, l_c[1]+y, l_c[1]+y, l_c[1]-y, l_c[1]-y]
        
        #ROI_RIGHT
        r_x = [r_c[0]+x, r_c[0]+x, r_c[0]-x, r_c[0]-x, r_c[0]+x]
        r_y = [r_c[1]-y, r_c[1]+y, r_c[1]+y, r_c[1]-y, r_c[1]-y]
        
        #ROI_CENTER
        c_x = [c_c[0]+x, c_c[0]+x, c_c[0]-x, c_c[0]-x, c_c[0]+x]
        c_y = [c_c[1]-y, c_c[1]+y, c_c[1]+y, c_c[1]-y, c_c[1]-y]
        
        #ROI FIX
        f_x = [(res[0] / 2)+30, (res[0] / 2)+30, (res[0] / 2)-30, (res[0] / 2)-30, (res[0] / 2)+30]
        f_y = [(res[1] / 2)-50, (res[1] / 2)+20, (res[1] / 2)+20, (res[1] / 2)-50, (res[1] / 2)-50]

        gazex = self.gazex
        gazey = self.gazey
        pupil = self.pupil
        time = self.time
        
        total = float(gazex.size)

        cut_l_y = np.logical_and(gazey > np.min(l_y), gazey < np.max(l_y))
        cut_l_x = np.logical_and(gazex > np.min(l_x), gazex < np.max(l_x))
        cut_l = np.logical_and(cut_l_y, cut_l_x)
        
        cut_r_y = np.logical_and(gazey > np.min(r_y), gazey < np.max(r_y))
        cut_r_x = np.logical_and(gazex > np.min(r_x), gazex < np.max(r_x))
        cut_r = np.logical_and(cut_r_y, cut_r_x)

        cut_c_y = np.logical_and(gazey > np.min(c_y), gazey < np.max(c_y))
        cut_c_x = np.logical_and(gazex > np.min(c_x), gazex < np.max(c_x))
        cut_c = np.logical_and(cut_c_y, cut_c_x)

        cut_f_y = np.logical_and(gazey > np.min(f_y), gazey < np.max(f_y))
        cut_f_x = np.logical_and(gazex > np.min(f_x), gazex < np.max(f_x))
        cut_f = np.logical_and(cut_f_y, cut_f_x)

        left = float(gazex[cut_l].size)
        right = float(gazex[cut_r].size)
        center = float(gazex[cut_c].size)
        fixation = float(gazex[cut_f].size)
        all_roi = float(center + left + right + fixation)

        per_roi = round(all_roi/total, 3) * 100
        per_left = round(left/total, 3) * 100
        per_right = round(right/total, 3) * 100
        per_center = round(center/total, 3) * 100
        per_fix = round(fixation/total, 3) * 100
        
        per_valid = round(float(self.endsize)/float(self.startsize) * 100, 2)
        blink_count = self.blink_count
        blink_rate = round(self.blink_rate, 2)
        
        fig, ax = plt.subplots()
        ax.scatter(gazex, gazey, c = time)
        ax.plot(l_x, l_y, c = 'r')
        ax.plot(r_x, r_y, c = 'r')
        ax.plot(c_x, c_y, c = 'r')
        ax.plot(f_x, f_y, c = 'r')
        ax.axis([0, res[0], 0, res[1]])
        fig.suptitle('% in ROI: {}'.format(per_roi))
        fig = plt.gcf()
        
        fig2, ax2 = plt.subplots()
        ax2.plot(time/1000, pupil)
        fig2.suptitle ('% valid: {}, blink count: {}, blink rate: {}'.format(per_valid, blink_count, blink_rate))
        fig2 = plt.gcf()
        
        self.qc_metrics = {'pct_roi_right' : [per_right],
                           'pct_roi_left' : [per_left],
                           'pct_roi_center' : [per_center],
                           'pct_roi_fix' : [per_fix],
                           'pct_any_roi' : [per_roi],
                           'pct_valid' : [per_valid],
                           'blink_count' : [blink_count],
                           'blink_rate' : [blink_rate]}
        
        self.graphs = (fig, fig2)
        

# In[TrackObject]:
        
class TrackObject:
    
    def __init__(self):
        self.subid = ''
        self.project_directory = ''
        self.tasklist = ['face1', 'face2']
        self.target_sampling_rate = 1.25
        self.native_sampling_rate = np.nan
        self.hasloaded = False
        self.run = {}
        for task in self.tasklist:
            self.run[task] = TrackData()
            
    @staticmethod
    def get_data(samples):
        gaze_x = samples['gaze_x']
        gaze_y = samples['gaze_y']
        pupil = samples['pupil']
            
        mspsamp = samples['time'][1] - samples['time'][0]
        
        time = np.arange(0, gaze_x.size * mspsamp, mspsamp)
        
        sampling_rate = 1000 / mspsamp
        
        return gaze_x, gaze_y, pupil, time, sampling_rate
        
    def write_to_missing(self, filepath, taskname):
        logpath = os.path.join(self.project_directory, 'missing_track_runs.csv')
        if not os.path.exists(logpath):
            f = open(logpath, 'w')
            f.write('subject, fmri, date_time, coins_path\n')
            f.close()
        datestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        outstr = '{},{},{},{}\n'.format(self.subid, taskname, datestr, filepath)
        f = open(logpath, 'a')
        f.write(outstr)
        f.close()
        
    def load_from_template(self, infile):
        infile = os.path.abspath(os.path.expanduser(infile))
        try:

            with open(infile) as json_data:
                d = json.load(json_data)
            for task in self.tasklist:
                taskfile = os.path.abspath(os.path.expanduser(d[task]))
                if os.path.isfile(taskfile) and d[task] != '':
                    print('loading: {}'.format(taskfile))
                    data = self.parse_asc(taskfile)
                    gazex, gazey, pupil, time, samprate = self.get_data(data)
                    self.run[task].gazex = gazex
                    self.run[task].gazey = gazey
                    self.run[task].pupil = pupil
                    self.run[task].time = time
                    self.run[task].org_start = time[0]
                    self.run[task].org_end = time[-1]
                    self.run[task].sampling_rate = samprate
                    print('Processing: {}, {}'.format(self.subid, task))
                    self.native_sampling_rate = samprate
                    self.run[task] = downsample(self.run[task], 4)
                    print('Blink Detection: ...')
                    self.run[task] = invalid(self.run[task])
                    self.run[task] = dilationspeed(self.run[task])
                    print('Blink Correction: ...')
                    self.run[task] = trendline(self.run[task])
                    print('Normalizing Pupil: ...')
                    self.run[task] = normalize(self.run[task])
                    print('Downsampling: ...')
                    self.run[task] = flipy(self.run[task])
                    self.run[task] = downsample(self.run[task], 800)
                    self.run[task].qc()
                elif not os.path.isfile(taskfile) and d[task] != '':
                    ostr = """-------------\nWarning!\n {} does not exist.\n
                    No tracking TSV file will be cretaed for {}, {}.\n-------------"""
                    print(ostr.format(taskfile, self.subid, task))
                    self.write_to_missing(taskfile, task)
            self.hasloaded=True
        except IOError:
            print('No file: {}'.format(infile))
        
    def parse_asc(self, edffile):
        cmd = 'edf2asc {}'.format(edffile)
        os.system(cmd)
        
        taskfile = edffile.rstrip('.edf')
        taskfile += '.asc'
        f = open(taskfile)
        asc = f.read()
        asc = asc.split('\n')
        
        asc_list = asc[:]
        for line in range(len(asc)):
            l = asc[line]
            if not is_number(l[:1]):
                asc_list.remove(l)
                
        asc = asc_list[:]
        
        d = {'time' : [], 'gaze_x' : [], 'gaze_y' : [], 'pupil' : []}
        
        for line in asc:
            
            line = line.split(' ')
            
            cont = True
            while cont:
                try:
                    line.remove('')
                except ValueError:
                    cont = False
                    
            for value in range(len(line)):
                line[value] = line[value].strip()
                
            cont = True
            while cont:
                try:
                    line.remove('')
                except ValueError:
                    cont = False
            
            new_line = []
            
            for value in range(len(line)):
                if is_number(line[value]):
                    new_line.append(float(line[value]))
                else:
                    if '/t' in line[value] or ' ' in line[value]:
                        num = line[value].split('\t')
                        num = ' '.join(num)
                        num = num.split(' ')
                        new_line.extend(num)
                    else:
                        new_line.append(line[value])
                        
            new_line2 = []
            
            for value in range(len(new_line)):
                if is_number(new_line[value]):
                    new_line2.append(float(new_line[value]))
                else:
                    num = new_line[value]
                    num = num.replace('.', ' -4000 ')
                    num = num.split(' ')
                    new_line2.extend(num)
                    
            cont = True
            while cont:
                try:
                    line.remove('')
                except ValueError:
                    cont = False
                    
            final_line = []
            
            for value in range(len(new_line2)):
                if is_number(new_line2[value]):
                    final_line.append(float(new_line2[value]))
                else:
                    final_line.append(-4000)
                    
            d['time'].append(final_line[0])
            d['gaze_x'].append(final_line[1])
            d['gaze_y'].append(final_line[2])
            d['pupil'].append(final_line[3])
            
        return pd.DataFrame(d)
        
    def save_track_csv(self, track_data, output_dir):
        output_csv = os.path.join(output_dir, 'tracking_values.csv')
        odat = {}
        odat['subject_id'] = track_data.subid
        for task in track_data.tasklist:
            odat[task+'_gazex'] = track_data.run[task].gazex
            odat[task+'_gazey'] = track_data.run[task].gazey
            odat[task+'_pupil'] = track_data.run[task].pupil
        df = pd.DataFrame([odat])
        if os.path.isfile(output_csv) is True:
            indf = pd.read_csv(output_csv)
            df = df.append(indf)
        print('Writing x/y/pup to: {}'.format(output_csv))
        df.to_csv(output_csv, index=False)
        
    def save_track_tsv(self, track_data, output_dir):
        tasklist = track_data.tasklist
        subid = track_data.subid[:9]
        subid2 = track_data.subid
        tsv_name = {}
        tsv_name['face1'] = subid+'_task-faces_run-01_tracking'
        tsv_name['face2'] = subid+'_task-faces_run-02_tracking'
        track_json = """{
            "SamplingFrequency": 1.25,
            "StartTime": 0.0,
            "Columns": ["gazex", "gazey", "pupil"]
            }"""
        for task in tasklist:
            gazex = track_data.run[task].gazex
            gazey = track_data.run[task].gazey
            pupil = track_data.run[task].pupil
            if gazex is not np.nan and gazey is not np.nan and pupil is not np.nan:
                outfile = os.path.join(output_dir, subid2, 'func', tsv_name[task]+'.tsv')
                print('Writing: {}'.format(outfile))
                k = []
                k.append(track_data.run[task].gazex[:])
                k.append(track_data.run[task].gazey[:])
                k.append(track_data.run[task].pupil[:])
                p = np.array(k)
                np.savetxt(outfile, p.transpose(), delimiter='\t')
                jsonpath = os.path.join(output_dir, subid2, 'func', tsv_name[task]+'.json')
                jsonfile = open(jsonpath, 'w')
                jsonfile.write(track_json)
                jsonfile.close()

                
    def plot_qc_graphs(self, track_data, output_dir):
        tasklist = track_data.tasklist
        subid = track_data.subid
        png_name = {}
        png_name['face1'] = subid+'_task-faces_run-01_tracking'
        png_name['face2'] = subid+'_task-faces_run-02_tracking'
        
        for task in tasklist:
            qc_metrics = track_data.run[task].qc_metrics
            graphs = track_data.run[task].graphs
            
            if qc_metrics != [] and graphs:
                
                gaze_plot = graphs[0]
                pupil_plot = graphs[1]
                
                pngpath = os.path.join(output_dir, png_name[task]+'_gaze.png')
                gaze_plot.savefig(pngpath, dpi=300)
                
                pngpath = os.path.join(output_dir, png_name[task]+'_pupil.png')
                pupil_plot.savefig(pngpath, dpi=300)
    
    def save_qc_csv(self, track_data, output_dir):
        tasklist = track_data.tasklist
        subid = track_data.subid
        csv_name = subid+'_qc-metrics.csv'
        csv_path = os.path.join(output_dir, csv_name)
        
        for task in tasklist:
            
            qc_metrics = track_data.run[task].qc_metrics
            
            if qc_metrics != []:
                
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                else:
                    df = pd.DataFrame({'pct_roi_right' : [],
                           'pct_roi_left' : [],
                           'pct_roi_center' : [],
                           'pct_roi_fix' : [],
                           'pct_any_roi' : [],
                           'pct_valid' : [],
                           'blink_count' : [],
                           'blink_rate' : []})
                    
                qc_metrics['task'] = task
                print(qc_metrics)
                new_df = pd.DataFrame(qc_metrics)
                
                final_df = df.merge(new_df, how = 'outer')
                final_df.to_csv(csv_path, index=False)
                    
                
        
        
