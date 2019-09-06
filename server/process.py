import random
import math
import signal
import sys
import threading

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.signal

import config
import server

freq = config.SAMPLE_RATE * np.fft.rfftfreq(config.WINDOW_SIZE)
spectra = None
start_id = 0
finish_id = 0
finished_processing = False


def start_processing():
    global start_id
    #print("start", start_id)
    start_id += 1
    job = threading.Thread(target=dft, args=[list(server.raw_data)])
    job.start()
    return job


def dft(dat):
    global finish_id
    if len(dat) != config.WINDOW_SIZE + config.AVG_W:
        finish_id += 1
        return None
    # TODO: better implementation
    hamming = scipy.signal.hamming(config.WINDOW_SIZE, False)
    ans = []
    for i in range(config.AVG_W):
        x = list(map(lambda x: x[0], dat[i:i+config.WINDOW_SIZE]))
        y = list(map(lambda x: x[1], dat[i:i+config.WINDOW_SIZE]))
        z = list(map(lambda x: x[2], dat[i:i+config.WINDOW_SIZE]))
        X = np.fft.rfft(x * hamming)
        Y = np.fft.rfft(y * hamming)
        Z = np.fft.rfft(z * hamming)
        ans.append(np.maximum(np.abs(X) ** 2, np.abs(Y)**2, np.abs(Z)**2))
    F = np.mean(ans, axis=0)
    global spectra
    spectra = F
    finish_id += 1
    global finished_processing
    finished_processing = True
    return freq, F


def get_avg(dat):
    return np.mean(dat[config.CUTOFF_POINT:])


def get_variance(dat):
    return np.var(dat[config.CUTOFF_POINT:])


def get_ratio(dat):
    sm = np.sum(dat[config.CUTOFF_POINT:])
    dat = dat[config.CUTOFF_POINT:]
    ans = []
    cnt = 0
    curr = 0
    for i in range(len(dat)):
        if cnt ==  config.BAND_RATIO_SIZE:
            
            cnt = 0
            ans.append(curr / sm)
            curr = 0
        curr += dat[i]
        cnt += 1
    # ignore the tailing end
    return ans

def get_features(dat):
    #
    # print(dat)
    return [get_avg(dat)] + [get_variance(dat)] + get_ratio(dat)