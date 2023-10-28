import multiprocessing as mp
import os, vtk, pyvista as pv, numpy as np
import time

import warnings
warnings.filterwarnings('ignore')

def gen_voxel(x, y, z):
    node_1 = [x, y, z]
    node_2 = [x+1, y, z]
    node_3 = [x+1, y+1, z]
    node_4 = [x, y+1, z]
    node_5 = [x, y, z+1]
    node_6 = [x+1, y, z+1]
    node_7 = [x+1, y+1, z+1]
    node_8 = [x, y+1, z+1]
    
    return [node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8]

def gen_mesh(densities, shape_shape):
    hide_indexes = []
    
    ex = shape_shape[0]
    ey = shape_shape[1]
    ez = shape_shape[2]
    
    for ez_ in range(ez):
        for ex_ in range(ex):
            for ey_ in range(ey):
                elem_index = (ex*ey)*ez_ + ey * ex_ + (ey - ey_ - 1)
                elem_index_hide = (ex*ey)*ez_ + ey * ex_ + ey_
                
                if (densities[elem_index] < np.quantile(densities, 0.6)):
                    hide_indexes.append(elem_index_hide)
    
    xrng = np.linspace(0, ex, ex+1, dtype=np.float32)
    yrng = np.linspace(0, ey, ey+1, dtype=np.float32)
    zrng = np.linspace(0, ez, ez+1, dtype=np.float32)
    
    x, y, z = np.meshgrid(xrng, yrng, zrng, indexing='xy')
    
    grid = pv.StructuredGrid(x, y, z)
    grid.hide_cells(hide_indexes, inplace = True)   
    
    return grid

def draw_densities(plotter, N_rows, N_cols, densities, space_shape):
    for irow in range(N_rows):
        for icol in range(N_cols):
            slot_id = irow * N_cols + icol
            if (densities[slot_id] == 'finished'):
                continue
            grid = gen_mesh(densities[slot_id], space_shape)
            
            plotter.subplot(irow, icol)
            plotter.add_mesh(grid.rotate_z(90), show_edges = True, color = '#A8A8A8', edge_color = 'black')
            plotter.show_bounds(color = 'black')

def visualizer_process(data_pipe, N_rows, N_cols, space_shape):
    n_slots = N_rows * N_cols
    n_voxels = space_shape[0] * space_shape[1] * space_shape[2]
    densities = [np.ones(n_voxels) for i in range(n_slots)]
    plotter = pv.Plotter(shape = (N_rows, N_cols), lighting = 'light kit')
    plotter.set_background('#39394A')
    
    # Visualizer initialization
    draw_densities(plotter, N_rows, N_cols, densities, space_shape)
    plotter.show(interactive_update = True)
    
    try:
        while True:
            if data_pipe.poll():
            
                densities = data_pipe.recv()
                if (densities.count('finished') == n_slots):
                    raise RuntimeError('No more data')
                
                plotter.clear()
                draw_densities(plotter, N_rows, N_cols, densities, space_shape)
                plotter.update()
                #time.sleep(1)
            
    except Exception as e:
        print(f'Visual process finalizing with {e}')
        plotter.close()
        return 
    
                
            
        