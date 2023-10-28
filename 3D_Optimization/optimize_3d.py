from fem_3d import *
#from problem_config import *
#from post_processor import *
import os

# Without filtering now
def optimize_3D(FEM_solver, config, verbose, data_pipe = None):
    iteration = 0
    
    ex = FEM_solver.ex
    ey = FEM_solver.ey
    ez = FEM_solver.ez
    
    x = np.ones(FEM_solver.n_elems) * config.vol_frac
    xPhys = x
    
    dense_c_norm = 1
    gamma = 1e-3

    while (dense_c_norm > config.dense_delta):
        iteration += 1
        if (verbose == True):
            print(f'Process {os.getpid()}: Iteration {iteration}, c-norm = {dense_c_norm:3.3f}', flush = True)
        
        # Matrix assembly with individual densities
        FEM_solver.assemble_sparse_K(xPhys, config.penalize, config.E_void, config.E0)
        
        # Displacements
        u = FEM_solver.solve_U()
        
        # Compliance, Sensitivity, Filtering
        c = 0
        dc = np.array([])
        dv = np.array([])
        
        for elem_index in range(FEM_solver.n_elems):
            # Individual compliance
            elem_dofs = FEM_solver.dofs_matrix[elem_index]
            
            young_modulus = config.E_void + pow(xPhys[elem_index], config.penalize) * (config.E0 - config.E_void)
            ce = np.dot(np.dot(u[elem_dofs].T, element_K(0.3)*young_modulus), u[elem_dofs])

            c += ce
            curr_dc = -config.penalize * (config.E0 - config.E_void) * pow(xPhys[elem_index], config.penalize - 1) * ce

            dc = np.append(dc, curr_dc)
            dv = np.append(dv, 1)
        
        # Optimality criteria
        lambda_1 = 0
        lambda_2 = 1e9

        x_new = np.zeros(x.shape)
        while ((lambda_2 - lambda_1) / (lambda_2 + lambda_1)) > 1e-3: #Binary search of lambda
            lambda_mid = (lambda_1 + lambda_2) / 2

            for i in range(x.shape[0]):
                B_e = np.sqrt(-dc[i] / (lambda_mid))
                if (x[i] * B_e <= max(0, x[i] - config.move)):
                    x_new[i] = max(0, x[i] - config.move)
                elif (x[i] * B_e >= min(1, x[i] + config.move)):
                    x_new[i] = min(1, x[i] + config.move)
                else:
                    x_new[i] = x[i] * B_e

            xPhys = x_new

            if (np.sum(xPhys) > config.vol_frac*FEM_solver.n_elems):
                lambda_1 = lambda_mid
            else:
                lambda_2 = lambda_mid
        
        # Checking Max iter
        if (iteration in config.save_iters):
            FEM_solver.save_config(xPhys, config.save_path + f'\\Design_{iteration}.txt')
        if (iteration == config.max_iter):
            break
            
        dense_c_norm = np.max(np.abs(x_new - x))
        x = x_new
        
        # Sending densities if running parallel
        if (data_pipe != None):
            data_pipe.send(x)
        
    return xPhys