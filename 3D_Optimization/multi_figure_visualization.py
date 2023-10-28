from post_processor import *

def add_figure(plotter, subplot_row, subplot_col, config, smooth_level, alpha = 0.9, save_name = None, save_stl = False):
    hide_indexes = []
    points = []
    
    for ez_ in range(config.ez):
        for ex_ in range(config.ex):
            for ey_ in range(config.ey):
                elem_index = (config.ex*config.ey)*ez_ + config.ey * ex_ + (config.ey - ey_ - 1)
                elem_index_hide = (config.ex*config.ey)*ez_ + config.ey * ex_ + ey_
                
                if (config.densities[elem_index] < 0.2):
                    hide_indexes.append(elem_index_hide)
                else:
                    points += gen_voxel(ex_, ey_, ez_)
    
    xrng = np.linspace(0, config.ex, config.ex+1, dtype=np.float32)
    yrng = np.linspace(0, config.ey, config.ey+1, dtype=np.float32)
    zrng = np.linspace(0, config.ez, config.ez+1, dtype=np.float32)
    
    x, y, z = np.meshgrid(xrng, yrng, zrng, indexing='xy')
    
    grid = pv.StructuredGrid(x, y, z)
    grid.hide_cells(hide_indexes, inplace = True)
    
    bounds_ = list(grid.bounds)
    
    padding = 5
    
    bounds_[0] -= padding
    bounds_[1] += padding
    bounds_[2] -= padding
    bounds_[3] += padding
    bounds_[4] -= padding
    bounds_[5] += padding
    
    pc = pv.PolyData(points)
    plotter.subplot(subplot_row, subplot_col)
    #plotter = pv.Plotter(lighting = 'light kit')
    
    if (smooth_level == 0):
        plotter.add_mesh(grid, 
                         show_edges = True,
                         edge_color = 'grey',
                         smooth_shading = False, 
                         color = '#3a3c3b')
    elif (smooth_level == 1):
        plotter.add_mesh(pc.delaunay_3d(alpha = alpha, offset = 12.5),
                         show_edges = False,
                         point_size = 0,
                         smooth_shading = False,
                         culling = False, 
                         show_vertices = False,
                         color = '#3a3c3b')
        
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


    plotter.show_bounds(color = 'black')
    
    #plotter.set_background(config.background_color)
    #plotter.show()

data_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data'

N_rows = 2
N_cols = 2
plotter = pv.Plotter(lighting = 'three lights', shape = (N_rows, N_cols))

paths_pool = [f'{data_path}\\Parallel\\Parallel_{i}.txt' for i in range(N_rows * N_cols)]
configs  = [read_config(path) for path in paths_pool]

for irow in range(N_rows):
    for icol in range(N_cols):
        add_figure(plotter, irow, icol, configs[irow*N_cols + icol], smooth_level = 1, save_name = None, save_stl = None)

plotter.set_background('grey')
plotter.show()