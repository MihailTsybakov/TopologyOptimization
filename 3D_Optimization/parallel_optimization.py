import multiprocessing as mp
from optimize_3d import *
import os

def optimizer_process(task_queue, output_pipe):
    try:
        while True:
            opti_task = task_queue.get(timeout = 1)
            print(f'Process {os.getpid()}: got task', flush = True)
            fem_solver = FEM_3D(opti_task.nx, opti_task.ny, opti_task.nz, opti_task.config.filter_R, opti_task.nu)
            
            for fixed_node in opti_task.fixes:
                fn_x = fixed_node[0]
                fn_y = fixed_node[1]
                fn_z = fixed_node[2]
                fix_x = bool(fixed_node[3])
                fix_y = bool(fixed_node[4])
                fix_z = bool(fixed_node[5])
                fem_solver.fix_node(fn_x, fn_y, fn_z, fix_x, fix_y, fix_z)
                
            for applied_load in opti_task.loads:
                al_x = applied_load[0]
                al_y = applied_load[1]
                al_z = applied_load[2]
                load_x = applied_load[3]
                load_y = applied_load[4]
                load_z = applied_load[5]
                fem_solver.apply_load(al_x, al_y, al_z, load_x, load_y, load_z)
                
            fem_solver.map_DOFs()
            print(f'Process {os.getpid()}: Problem formulated. Finite elements: {fem_solver.n_elems}', flush = True)
            
            densities = optimize_3D(fem_solver, opti_task.config, True, output_pipe)
            
            fem_solver.save_config(densities, opti_task.save_path)
            
    except Exception as e:
        output_pipe.send(f'Finished with {e}')
        return
        