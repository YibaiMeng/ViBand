import random
import math
import signal
import sys
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import config
import server
import process
import svm_eval
import presentation

anim = None  # animation handler


def register_sigint_handler():
    def handler(signum, frame):
        global anim
        print('[signal handler]: calling server.stop_server')
        server.stop_server()
        print('[signal handler]: server stopped')
        presentation.start_presentation_server()
        # anim.event_source.stop()
        # plt.close()
        sys.exit()
    signal.signal(signal.SIGINT, handler)


def draw_dft():
    fig = plt.figure()
    ax = plt.axes(xlim=(50, config.SAMPLE_RATE * 1 / 2))
    line, = ax.plot([], [], lw=3) 

    def init():
        line.set_data([], [])
        return line,

    def animate(i):
        line.set_data(process.freq, process.spectra)
        return line,
    global anim
    anim = animation.FuncAnimation(fig, animate, interval=100)
    plt.show()


register_sigint_handler()
server.start_server()
svm_eval.load_trained_models()
#presentation.start_presentation_server()
time.sleep(3)
#with open(sys.argv[1],"w") as fp:
while True:
    feat = process.get_features(process.spectra)
    res = svm_eval.eval(feat)
    if res[0] == 1:
        #presentation.next_page()
        print("Next Page!")
    elif res[0] == 2:
        #presentation.prev_page()
        print("Prev page!")
    #fp.write(str(feat))
    time.sleep(0.1)
# draw_dft()
