from optimize_2d import *
from parallel_optimization import *
from plotter_process import *
from matplotlib import pyplot as plt

import random, warnings
warnings.filterwarnings('ignore')

plt.style.use('dark_background')

# 4 Parallel jobs
N_tasks = 12

if __name__ == '__main__':
    tasks_queue = mp.Queue()
    
    # Setting up pipes for density maps
    pipe_1_main, pipe_1_proc = mp.Pipe()
    pipe_2_main, pipe_2_proc = mp.Pipe()
    pipe_3_main, pipe_3_proc = mp.Pipe()
    pipe_4_main, pipe_4_proc = mp.Pipe()
    
    pipe_visual_home, pipe_visual_proc = mp.Pipe()
    
    process_1 = mp.Process(target = optimizer_process, args = (tasks_queue, pipe_1_proc, ))
    process_2 = mp.Process(target = optimizer_process, args = (tasks_queue, pipe_2_proc, ))
    process_3 = mp.Process(target = optimizer_process, args = (tasks_queue, pipe_3_proc, ))
    process_4 = mp.Process(target = optimizer_process, args = (tasks_queue, pipe_4_proc, ))
    
    process_visual = mp.Process(target = visualize, args = (pipe_visual_proc, (49, 49), ))
    
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
        
    process_1.start()
    process_2.start()
    process_3.start()
    process_4.start()
    process_visual.start()
    
    density_map_1 = np.ones((49, 49)) * 0.25
    density_map_2 = np.ones((49, 49)) * 0.25
    density_map_3 = np.ones((49, 49)) * 0.25
    density_map_4 = np.ones((49, 49)) * 0.25    
    
    finished = 0
    while finished < 4:
        data_1_poll = pipe_1_main.poll()
        data_2_poll = pipe_2_main.poll()
        data_3_poll = pipe_3_main.poll()
        data_4_poll = pipe_4_main.poll()
        
        if (data_1_poll == True):
            density_map_1 = pipe_1_main.recv()
            if (density_map_1 == 'finished'):
                finished += 1
            
        if (data_2_poll == True):
            density_map_2 = pipe_2_main.recv()
            if (density_map_2 == 'finished'):
                finished += 1
            
        if (data_3_poll == True):
            density_map_3 = pipe_3_main.recv()
            if (density_map_3 == 'finished'):
                finished += 1
            
        if (data_4_poll == True):
            density_map_4 = pipe_4_main.recv()
            if (density_map_4 == 'finished'):
                finished += 1
        
        data_package = DataPackage('density', [density_map_1, density_map_2, density_map_3, density_map_4])    
        if (finished == 4):
            data_package.ptype = 'stop'
            
        pipe_visual_home.send(data_package)
            
            
    process_1.join()
    process_2.join()
    process_3.join()
    process_4.join()
    process_visual.join()
    
    plt.close()