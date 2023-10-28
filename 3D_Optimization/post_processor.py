import os
import vtk
import numpy as np
import pyvista as pv

data_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data'
blender_path = 'C:\\Program Files\\Blender Foundation\\Blender 3.2'
stl_script_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Code\\STL_Smooth_Script.py'

class Visualizer_Config():
    def __init__(self, nx, ny, nz, ex, ey, ez, points, points_data, densities):
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.ex = ex
        self.ey = ey
        self.ez = ez
        self.points = points
        self.densities = densities
        self.points_data = points_data
        
        self.draw_edges = True
        self.colormap = 'jet'
        
def read_config(filename):
    input_file = open(filename, 'r')
    
    data = input_file.read()
    data_segments = data.split('section\n')
    
    node_numbers = data_segments[0].split(' ')
    displacements = data_segments[1].split('\n')
    densities_data = data_segments[2].split('\n')
    
    nx = int(node_numbers[0])
    ny = int(node_numbers[1])
    nz = int(node_numbers[2])
    ex = nx-1
    ey = ny-1
    ez = nz-1
    
    x_points = np.linspace(0, nx, nx)
    y_points = np.linspace(0, ny, ny)
    z_points = np.linspace(0, nz, nz)
    
    points = []
    points_data = []
    densities = []
    
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                point = [nx, ny, nz]
                index = x * (ny*nz) + nz*y + z
                point_displs = displacements[index].split(' ')
                dx = float(point_displs[0])
                dy = float(point_displs[1])
                dz = float(point_displs[2])
                
                points.append(point)
                points_data.append([dx, dy, dz])
    
    for ex_ in range(ex):
        for ey_ in range(ey):
            for ez_ in range(ez):
                elem_index = ex_ * (ey*ez) + ez*ey_ + ez_
                density = float(densities_data[elem_index])
                densities.append(density)
                
    config = Visualizer_Config(nx, ny, nz, ex, ey, ez, points, points_data, densities)
    
    input_file.close()
    
    return config


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

def visualize(config, smooth_level, alpha = 0.9, save_name = None, save_stl = False):
    hide_indexes = []
    points = []
    
    for ez_ in range(config.ez):
        for ex_ in range(config.ex):
            for ey_ in range(config.ey):
                elem_index = (config.ex*config.ey)*ez_ + config.ey * ex_ + (config.ey - ey_ - 1)
                elem_index_hide = (config.ex*config.ey)*ez_ + config.ey * ex_ + ey_
                
                if (config.densities[elem_index] < 0.5):
                    hide_indexes.append(elem_index_hide)
                else:
                    points += gen_voxel(ex_, ey_, ez_)
    
    xrng = np.linspace(0, config.ex, config.ex+1, dtype=np.float32)
    yrng = np.linspace(0, config.ey, config.ey+1, dtype=np.float32)
    zrng = np.linspace(0, config.ez, config.ez+1, dtype=np.float32)
    
    x, y, z = np.meshgrid(xrng, yrng, zrng, indexing='xy')
    
    grid = pv.StructuredGrid(x, y, z)
    grid.hide_cells(hide_indexes, inplace = True)
    '''
    grid.plot(show_edges = True,
              show_axes = False,
              background = 'black',
              color = 'white',
              show_bounds = True,
              padding = 0.1)
    '''
    bounds_ = list(grid.bounds)
    
    padding = 5
    
    bounds_[0] -= padding
    bounds_[1] += padding
    bounds_[2] -= padding
    bounds_[3] += padding
    bounds_[4] -= padding
    bounds_[5] += padding
    
    pc = pv.PolyData(points)
    plotter = pv.Plotter(lighting = 'light kit')
    
    if (smooth_level == 0):
        plotter.add_mesh(grid, 
                         show_edges = True,
                         color = config.mesh_color,
                         edge_color = 'grey',
                         smooth_shading = False)
    elif (smooth_level == 1):
        plotter.add_mesh(pc.delaunay_3d(alpha = alpha, offset = 12.5),
                         show_edges = False,
                         color = config.mesh_color,
                         point_size = 0,
                         smooth_shading = False,
                         culling = False, 
                         show_vertices = False)
        if (save_name != None):
            plotter.export_gltf(save_name)
            if (save_stl == True):
                shell_command = f'""{blender_path}\\blender" --background --python "{stl_script_path}""'
                os.system(shell_command)
        
    elif (smooth_level == 2):
        plotter.add_mesh(pc.delaunay_3d(alpha = alpha, offset = 12.5),
                         show_edges = False,
                         color = config.mesh_color,
                         point_size = 0,
                         smooth_shading = True,
                         culling = False, 
                         show_vertices = False,
                         opacity = 1.0)


    plotter.show_bounds(bounds = bounds_,
                        color = config.bounds_color)
    
    plotter.set_background(config.background_color)
    plotter.show()
    
path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data\\Arm_4_2.txt'
path_data = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data'

config = read_config(path)

config.mesh_color = 'lightblue'
config.background_color = 'black'
config.bounds_color = 'white'

#visualize(config, smooth_level = 2, alpha = 0.9, save_name = None, save_stl = False)