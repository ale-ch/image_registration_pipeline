#!/usr/bin/env python

import nd2
import pickle
import numpy as np
import h5py

"""
Pickle
"""
def save_pickle(object, path):
    # Open a file in binary write mode
    with open(path, 'wb') as file:
        # Serialize the object and write it to the file
        pickle.dump(object, file)

def load_pickle(path):
    # Open the file in binary read mode
    with open(path, 'rb') as file:
    # Deserialize the object from the file
        loaded_data = pickle.load(file)

    return loaded_data

"""
h5
"""
def save_h5(data, path):
        # Save the NumPy array to an HDF5 file
    with h5py.File(path, 'w') as hdf5_file:
        hdf5_file.create_dataset('dataset', data=data)
        
def load_h5(path, channels_to_load=None):
    # Read the NumPy array from the HDF5 file
    with h5py.File(path, 'r') as hdf5_file:
        data = hdf5_file['dataset'][:]

        if channels_to_load is not None:
            data = data[:, :, channels_to_load]

    return data

def load_h5_channels(path, channels_to_load):
    # Open the HDF5 file
    with h5py.File(path, 'r') as f:
        # Access the dataset
        dataset = f['dataset']
        # Use slicing to load only the specific channels
        data = dataset[:, :, channels_to_load]
    
        return data

"""
nd2
"""
def load_nd2(file_path):
    """
    Read an ND2 file and return the image array.
    
    Parameters:
    file_path (str): Path to the ND2 file
    
    Returns:
    numpy.ndarray: Image data
    """
    with nd2.ND2File(file_path) as nd2_file:
        data = nd2_file.asarray()
        data = data.transpose((1, 2, 0))
        
    return data
