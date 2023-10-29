from optimize_2d import *
from parallel_optimization import *
from plotter_process import *
from matplotlib import pyplot as plt

import random, warnings
warnings.filterwarnings('ignore')

plt.style.use('dark_background')

N_rows = 3
N_cols = 3

# Optimizer tasks
N_tasks = 12

if __name__ == '__main__':
    tasks_queue = mp.Queue()
    
    # Process number = N_rows * N_cols
    n_processes = N_rows * N_cols
    
    # Setting up data pipes
    pipes = [mp.Pipe() for i in range(n_processes)]
    
    # Setting up pipe for visual proces
    pipe_visual_home, pipe_visual_proc = mp.Pipe()
    
    # Pipe[0] = Home side, Pipe[1] = Process side
    process_pool = [mp.Process(target = optimizer_process, args = (tasks_queue, pipes[i][1], )) for i in range(n_processes)]
    
    # Visualizer process
    process_visual = mp.Process(target = visualize, args = (pipe_visual_proc, (49, 49), (N_rows, N_cols), ))
    
    # Loading opti tasks
    meshes = [QuadMesh(50, 50) for i in range(N_tasks)]
    config = Config()
    for i in range(N_tasks):
        task = OptimizationTask(meshes[i], volume_frac = 0.25, max_iter = 18, config = config)
        task.fix_node(49, 49, True, True)
        task.fix_node(49, 0, True, True)
        load_x = random.randint(0, 20)
        load_y = random.randint(0, 49)
        task.apply_load(load_x, load_y, 0, -1)
        
        tasks_queue.put(task)
        
    for i in range(n_processes):
        process_pool[i].start()
    process_visual.start()
    
    density_maps = [np.ones((49, 49)) for i in range(n_processes)]
    
    finished = 0
    while finished < n_processes:
        for i in range(n_processes):
            if (pipes[i][0].poll() == True):
                density_map = pipes[i][0].recv()
                if (density_map == 'finished'):
                    finished += 1
                density_maps[i] = density_map
        
        data_package = DataPackage('density', density_maps)    
        if (finished == n_processes):
            data_package.ptype = 'stop'
            
        pipe_visual_home.send(data_package)
            
            
    # Joining
    for i in range(n_processes):
        process_pool[i].join()
    process_visual.join()
    
    plt.close()