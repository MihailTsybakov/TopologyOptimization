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

def visualize(data_pipe, subplots_shape):
    fig, axes = plt.subplots(1, 4, figsize = (11, 11))
    
    # Prev step densities
    density_1_old = np.ones(subplots_shape)
    density_2_old = np.ones(subplots_shape)
    density_3_old = np.ones(subplots_shape)
    density_4_old = np.ones(subplots_shape)
    
    slice_factors = np.linspace(0, 1, 20).reshape(20, 1, 1)
    
    try:
        while True:
            if not data_pipe.poll():
                continue
            
            data_pack = data_pipe.recv()
            
            if (data_pack.ptype == 'stop'):
                plt.close()
                return
            
            density_1_new = data_pack.data[0]
            density_2_new = data_pack.data[1]
            density_3_new = data_pack.data[2]
            density_4_new = data_pack.data[3]
            
            slices_1 = density_1_old + (density_1_new - density_1_old) * slice_factors
            slices_2 = density_2_old + (density_2_new - density_2_old) * slice_factors
            slices_3 = density_3_old + (density_3_new - density_3_old) * slice_factors
            slices_4 = density_4_old + (density_4_new - density_4_old) * slice_factors
            
            for i in range(20):
                axes[0].clear()
                axes[1].clear()
                axes[2].clear()
                axes[3].clear()
                axes[0].imshow(slices_1[i], interpolation = 'gaussian', cmap = 'jet')
                axes[1].imshow(slices_2[i], interpolation = 'gaussian', cmap = 'jet')
                axes[2].imshow(slices_3[i], interpolation = 'gaussian', cmap = 'jet')
                axes[3].imshow(slices_4[i], interpolation = 'gaussian', cmap = 'jet')
                plt.pause(0.001)
                
            density_1_old = density_1_new
            density_2_old = density_2_new
            density_3_old = density_3_new
            density_4_old = density_4_new
                
    except Exception as e:
        print(f'{e}')
        return