import multiprocessing as mp
from matplotlib import pyplot as plt
import numpy as np

import warnings, time

warnings.filterwarnings('ignore')
plt.style.use('dark_background')

# Data + Flag wrapper
class DataPackage():
    def __init__(self, package_type, package_data):
        self.ptype = package_type
        self.data = package_data

def visualize(data_pipe, subplots_shape, grid_shape):
    fig, axes = plt.subplots(grid_shape[0], grid_shape[1], figsize = (11, 11))
    
    n_proc = grid_shape[0] * grid_shape[1]
    
    try:
        while True:
            if not data_pipe.poll():
                continue
            
            data_pack = data_pipe.recv()
            
            if (data_pack.ptype == 'stop'):
                plt.close()
                return
            
            densities_new = data_pack.data
            
            for irow in range(grid_shape[0]):
                for icol in range(grid_shape[1]):
                    axes[irow][icol].clear()
                    slice_i = irow*grid_shape[1] + icol
                    if (densities_new[slice_i] == 'finished'):
                        continue
                    axes[irow][icol].imshow(densities_new[slice_i], interpolation = 'gaussian', cmap = 'jet')
            plt.pause(0.01)
                
    except Exception as e:
        print(f'{e}')
        return