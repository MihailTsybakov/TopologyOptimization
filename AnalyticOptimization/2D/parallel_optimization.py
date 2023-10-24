from optimize_2d import *
import multiprocessing as mp
import os, time

def optimizer_process(task_queue, output_pipe):
    # Gets optimization task from pipe and sends
    # Optimization results at each iteration
    try:
        while True:
            optimizer = Optimizer_2D(verbose_level = 0, optimizer_ID = f'Optimizer [{os.getpid()}]')
            opti_task = task_queue.get(timeout = 1) # 1 second timeout
            print(f'Process Id {os.getpid()}: Got task')
            optimizer.set_up(opti_task)
            optimizer.optimize(multiprocess_pipe = output_pipe)
            time.sleep(0.1)                         # For result checking
    except Exception as e:
        output_pipe.send('finished')
        print(f'Process Id {os.getpid()}: {e} finalizing.')
        return