import numpy as np
from matplotlib import pyplot as plt
import h5py
from os import listdir
from os.path import isfile, join
import argparse
import statistics as stats

#Size of LTE subframe in samples at 7.68MHz
FRAME_SIZE = 7680

class SDR:

    # init method or constructor
    def __init__(self, rx):
        self.rx = rx
        self.files = []
        self.pos = []
        self.ant1 = []
        self.ant2 = []
        self.pos_diffs = []
        self.pos_med = 0
        self.rssi = []
        self.devl = []
        self.rxl = []
        self.locl = []

    def add_files(self, file):
        self.files.append(file)

    def open_pos(self, args, index):
        self.pos = open(args.base_path + self.files[index][0], 'r').read().splitlines()
        self.pos = [int(x) for x in self.pos]
        #Calculates samples between frames and remove any frames that are too detected at an irregular interval (Most likely noise)
        self.pos_diffs = [j-i for i, j in zip(self.pos[:-1], self.pos[1:])]
        diff_median = stats.median(self.pos_diffs)
        self.pos = [x for x, y in zip(self.pos, self.pos_diffs) if abs(y - diff_median) < 500]
        self.pos_diffs = [y for y in self.pos_diffs if abs(y - diff_median) < 500]

    def parse_ants(self, args, index):
        self.ant1 = np.fromfile(args.base_path + self.files[index][1], dtype=np.complex64).tolist()
        self.ant2 = np.fromfile(args.base_path + self.files[index][2], dtype=np.complex64).tolist()
        self.ant1 = [self.ant1[x - args.buffer:x + args.buffer + FRAME_SIZE] for x in self.pos]
        self.ant2 = [self.ant2[x - args.buffer:x + args.buffer + FRAME_SIZE] for x in self.pos]
        if (args.plot_frames):
            plt.plot(np.abs(self.ant1[0]))
            plt.plot(np.abs(self.ant2[0]))
            if (args.debug):
                plt.plot(np.abs(self.ant1[10]))
                plt.plot(np.abs(self.ant2[10]))

    def calc_rssi(self, args):
        for raw_frame in self.ant1:
            rssi = sum([x.imag**2 + x.real**2 for x in raw_frame]) / len(raw_frame)
            rssi_dbm = 10 * np.log10(rssi) + 30
            if (args.debug):
                print("RSSI: ", rssi)
                print("RSSI in dbm: ", rssi_dbm)
            self.rssi.append(rssi_dbm)

    def make_labels(self, index):
        suffix = self.files[index][0].replace("lteframepos", '')
        rx = int(suffix[-1])
        dev = int(suffix[-3])
        yloc = float(suffix[5:9])
        xloc = float(suffix[0:4])
        num_samples = len(self.pos)
        self.rxl = [rx] * num_samples
        self.devl = [dev] * num_samples
        self.locl = [[xloc, yloc]] * num_samples

    def clear_values(self):
        self.pos = []
        self.ant1 = []
        self.ant2 = []
        self.pos_diffs = []
        self.pos_med = 0
        self.rssi = []
        self.devl = []
        self.rxl = []
        self.locl = []

