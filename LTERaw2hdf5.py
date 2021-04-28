import numpy as np
import h5py
from os import listdir
from os.path import isfile, join
import argparse
import timeit
from itertools import groupby
from RXClass import SDR

def lte_main(args):
    # Load all Files from folder
    pos_files = [f for f in listdir(args.base_path) if isfile(join(args.base_path, f)) and
                f.startswith("lteframepos")]
    ant1_files = [f for f in listdir(args.base_path) if isfile(join(args.base_path, f)) and
                  f.startswith("lte_ant1_")]
    ant2_files = [f for f in listdir(args.base_path) if isfile(join(args.base_path, f)) and
                  f.startswith("lte_ant2_")]

    # Sort files and ensure they match/nothing is missing
    pos_files.sort()
    ant1_files.sort()
    ant2_files.sort()
    pos_suffix = [pos.replace("lteframepos", '') for pos in pos_files]
    ant1_suffix = [ant1.replace("lte_ant1_", '') for ant1 in ant1_files]
    ant2_suffix = [ant2.replace("lte_ant2_", '') for ant2 in ant2_files]
    if (pos_suffix != ant1_suffix or pos_suffix != ant2_suffix):
        raise(Exception("Mismatched files"))

    #Compute the number of collections present and instantiate SDR objects
    num_collects = len(pos_files) / args.num_sdr
    sdrs = []
    for rx in range(args.num_sdr):
        sdrs.append(SDR(rx))

    #Assigns the files belonging to the SDR to the object
    for rx, files in groupby(zip(pos_files, ant1_files, ant2_files), lambda x: x[-1]):
        for file in files:
            sdrs[int(rx[-1])].add_files(file)

    #Create Output File for later
    out_file = h5py.File(args.base_path + "LTEtrain.hdf5", 'w')
    total_ant1 = out_file.create_dataset('ant1Train', shape=(0, 7680 + args.buffer * 2), dtype=np.complex64, chunks=True,
                                         compression='lzf', maxshape=(None, None))
    total_ant2 = out_file.create_dataset('ant2Train', shape=(0, 7680 + args.buffer * 2), dtype=np.complex64, chunks=True,
                                         compression='lzf', maxshape=(None, None))
    total_rssi = out_file.create_dataset('powTrain', shape=(0,), dtype=np.float64, chunks=True, compression='lzf', maxshape=(None,))
    total_dev = out_file.create_dataset('dev_labels', shape=(0,), dtype=np.uint8, chunks=True, compression='lzf', maxshape=(None,))
    total_loc = out_file.create_dataset('loc_labels', shape=(0,2), dtype=np.float16, chunks=True, compression='lzf', maxshape=(None, 2))
    total_rx = out_file.create_dataset('rx_labels', shape=(0,), dtype=np.uint8, chunks=True, compression='lzf', maxshape=(None,))
    total_pos = out_file.create_dataset('posTrain', shape=(0,), dtype=np.uint64, chunks=True, compression='lzf', maxshape=(None,))
    #Collect_indx in this case is a single collection
    for collect_indx in range(num_collects):

        #Opens the position files and finds the SDR that captured the least
        start_time = timeit.default_timer()
        num_cap = []
        for sdr in sdrs:
            sdr.open_pos(args, collect_indx)
            num_cap.append(len(sdr.pos))
        least_cap = np.argmin(num_cap)
        if (args.debug):
            print("SDR with least number of frames is", least_cap)

        #This matches the frames between SDRs
        #The number of frames from the SDR that captured the least is the range
        #For every other SDR, it runs the range over the frames positions until it finds the point that best matches
        #Then remove all frames outside that range from each SDR
        big_sdrs = [y for x,y in enumerate(sdrs) if x != least_cap]
        for sdr in big_sdrs:
            size_diff = len(sdr.pos) - len(sdrs[least_cap].pos)
            if (size_diff):
                l1_diff = []
                for i in range(size_diff):
                    l1_diff.append(sum(abs(sdr.pos[i:size_diff+i] - sdrs[least_cap].pos)))
                best_indx = np.argmin(l1_diff)
                if (args.debug):
                    print("SDR " + str(sdr.rx) + " offset:", best_indx)
                    print("SDR " + str(sdr.rx) + " difference:", min(l1_diff))
                sdr.pos = sdr.pos[best_indx:size_diff+best_indx]

        #Can now begin parsing frames from each antenna and calculating RSSI
        for sdr in sdrs:
            sdr.parse_ants(args, collect_indx)
            #args.num_save specifies upper bound of frames collected
            if (len(sdr.ant1) > args.num_save):
                sdr.ant1 = sdr.ant1[:args.num_save]
                sdr.ant2 = sdr.ant2[:args.num_save]
                sdr.pos = sdr.pos[:args.num_save]
            sdr.calc_rssi(args)

            #Add location to dataset and make labels
            #clear values for next run
            sdr.make_labels(collect_indx)
            total_ant1.resize((total_ant1.shape[0] + len(sdr.ant1)), axis=0)
            total_ant1[-len(sdr.ant1):] = sdr.ant1
            total_ant2.resize((total_ant2.shape[0] + len(sdr.ant2)), axis=0)
            total_ant2[-len(sdr.ant2):] = sdr.ant2
            total_rssi.resize((total_rssi.shape[0] + len(sdr.rssi)), axis=0)
            total_rssi[-len(sdr.rssi):] = sdr.rssi
            total_pos.resize((total_pos.shape[0] + len(sdr.pos)), axis=0)
            total_pos[-len(sdr.pos):] = sdr.pos
            total_dev.resize((total_dev.shape[0] + len(sdr.devl)), axis=0)
            total_dev[-len(sdr.devl):] = sdr.devl
            total_loc.resize((total_loc.shape[0] + len(sdr.locl)), axis=0)
            total_loc[-len(sdr.locl):] = sdr.locl
            total_rx.resize((total_rx.shape[0] + len(sdr.rxl)), axis=0)
            total_rx[-len(sdr.rxl):] = sdr.rxl

            sdr.clear_values()
        elapsed_time = timeit.default_timer() - start_time
        print("File " + sdr.files[collect_indx][0][11:] + " completed in " + str(elapsed_time) + " seconds")

    print("Done")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Takes 5 files (file sink, file sink header, parse data, and '
                                                 'CSI data and organizes them into a text file where each lline corresponds to a single frame')
    parser.add_argument('-base_path', action='store', default="/home/nij/GNU/RawData/", dest='base_path',
                        help='Path to all files')
    parser.add_argument('-p', action='store_true', default=False, dest='plot_frames',
                        help='Plots frames in matplotlib to appear on screen')
    parser.add_argument('-n', action='store', type=int, default=2000, dest='num_save',
                        help='The upper bound of how many frames will be saved to file')
    parser.add_argument('-d', action='store_true', default=False, dest='debug', help='Turns on debug mode')
    parser.add_argument('-b', action='store', type=int, default=500, dest='buffer',
                        help='Number of samples to save before and after frame')
    parser.add_argument('-sdr', action='store', type=int, default=4, dest='num_sdr',
                        help='Number of SDRs used in data collection')
    args = parser.parse_args()

    lte_main(args)