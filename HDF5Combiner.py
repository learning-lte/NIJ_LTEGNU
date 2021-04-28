import h5py
import numpy as np
import argparse
from os import listdir

def combine_main(args):

    #Finds all .hdf5 files in target folder
    file_list = listdir(args.store_path)
    file_list = [x for x in file_list if x.endswith(".hdf5")]
    if (args.save_path + args.new_name in file_list):
        file_list.remove(args.save_path + args.new_name)

    #Creates new hdf5 file. Copies the first datasets to this new file and appends the rest
    f1 = h5py.File(args.save_path + args.new_name, 'a')
    for file in file_list:
        with h5py.File(args.store_path + file, 'r') as f2:
            for dataset in f2.keys():
                if dataset in f1.keys():
                    f1[dataset].resize((f1[dataset].shape[0] + f2[dataset].shape[0]), axis=0)
                    f1[dataset][-f2[dataset].shape[0]:] = f2[dataset]
                else:
                    f2.copy(dataset, f1)
        f2.close()
    num_samples = f1[f1.keys()[0]].shape[0]
    f1.close()
    print("Done")
    print("Final File contains " + str(num_samples) + " samples")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Takes 5 files (file sink, file sink header, parse data, and '
                                                 'CSI data and organizes them into a text file where each lline corresponds to a single frame')
    parser.add_argument('-store_path', action='store', default="/home/nij/GNU/RawData/", dest='store_path',
                        help='Path to existing files to be combined')
    parser.add_argument('-save_path', action='store', default="/home/nij/GNU/RawData/", dest='save_path',
                        help='Path to new saved file')
    parser.add_argument('-b', action='store', type=int, default=500, dest='buffer',
                        help='Number of samples saved before and after frame')
    parser.add_argument('-name', action='store', default="newDataset.hdf5", dest='new_name',
                        help='Name for new file')
    args = parser.parse_args()

    combine_main(args)