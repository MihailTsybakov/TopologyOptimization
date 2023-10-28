from parallel_optimization import *
from problem_config import *
from opti_task import *
from visual_process import *

import warnings, random
warnings.filterwarnings('ignore')

N_rows = 2
N_cols = 2

n_processes = N_rows * N_cols

N_tasks = 4

nx = 25
ny = 25
nz = 25

config = Config()
config.nx = nx
config.ny = ny
config.nz = nz
config.vol_frac = 0.07
config.penalize = 3
config.dense_delta = 0.01
config.move = 0.2
config.filter_R = 1.5
config.E_void = 1e-9
config.E0 = 1
config.max_iter = 12
config.save_iters = [1, 2, 5, 10, 15, 20]
config.save_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data'

save_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data'

if __name__ == '__main__':
    task_queue = mp.Queue()
    
    pipes = [mp.Pipe() for i in range(n_processes)]
    visual_pipe_home, visual_pipe_proc = mp.Pipe()
    
    # Pipe[i][0] = Home Side, Pipe[i][1] = Process Side
    process_pool = [mp.Process(target = optimizer_process, args = (task_queue, pipes[i][1], )) for i in range(n_processes)]
    visual_process = mp.Process(target = visualizer_process, args = (visual_pipe_proc, N_rows, N_cols, (nx-1, ny-1, nz-1), ))
    
    for i in range(N_tasks):
        fixed_nodes = [
            [2, 24, 2, 1, 1, 1],
            [2, 24, 22, 1, 1, 1],
            [22, 24, 2, 1, 1, 1],
            [22, 24, 22, 1, 1, 1]
        ]
        loaded_x = 11
        loaded_y = 0
        loaded_z = 5*i
        
        applied_loads = [
            [loaded_x, loaded_y, loaded_z, 0, 0, -1]
        ]
        
        new_task = OptiTask(nx, ny, nz, 0.3, config, fixed_nodes, applied_loads, f'{save_path}\\Parallel\\Parallel_{i}.txt')
        
        task_queue.put(new_task)
    
    for i in range(n_processes):
        print(f'Launching process {i+1}', flush = True)
        process_pool[i].start()
    visual_process.start()
             
    finished = 0
    densities = [np.ones((nx-1)*(ny-1)*(nz-1)) for i in range(n_processes)]
    
    new_data = [1 for i in range(n_processes)]
    
    while finished < n_processes:
        for i in range(n_processes):
            if (pipes[i][0].poll() == True):
                new_data[i] = 1
                density_map = pipes[i][0].recv()
                if (density_map == 'finished'):
                    finished += 1
                densities[i] = density_map
                
        if (new_data.count(1) == n_processes):
            visual_pipe_home.send(densities)
            new_data = [0 for i in range(n_processes)]
        
    for i in range(n_processes):
        process_pool[i].join()
    visual_process.join()
    
    