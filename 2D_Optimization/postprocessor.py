# Postprocessing routines for topology optimal designs

from matplotlib import pyplot as plt
import numpy as np

class Postprocessor:
    def __init__(self):
        self.design = None
        
    def load_density_matrix(self, load_path):
        self.design = np.loadtxt(load_path)
        self.ey = self.design.shape[0]
        self.ex = self.design.shape[1]
        
    def draw_design(self):  
        plt.style.use('dark_background')
        plt.imshow(self.design, interpolation = 'gaussian', cmap = 'twilight_shifted')
        plt.show()    