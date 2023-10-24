# Module for 2D Topology Optimziation

# ==== Usage ====
#
# 1. Build mesh
# 2. Instantiate config object
# 3. Create and specify OptimizeTask object
# 4. Fix nodes, apply loads via task
# 5. Instantiate Optimizer_2D object
# 6. Call set_up() function - prepares filter, FEM_solver, etc.
# 7. Call optimize() function
# 8. Draw / Save results

from fem_2d import *
from opti_task import *

import math

class Optimizer_2D:
    def __init__(self, verbose_level, optimizer_ID):
        # Verbose levels:
        # 0 = silent
        # 1 = minimum info
        # 2 = maximum info
        
        # Optimzier Id for multithreaded optimizations
        
        self.log_level = verbose_level
        self.ID = optimizer_ID
        
    def log_event(self, message, log_priority):
        if (log_priority <= self.log_level):
            print(f' <logs> <optimizer ID = {self.ID}> \t{message}')
        
    def set_up(self, task: OptimizationTask):
        self.task = task
        
        # DOFs mapping
        task.mesh.map_dofs()
        self.log_event('DOFs mapped', 2)
        
        # Setting up solver with mesh, DOFs already mapped
        self.FEM_solver = FEM_2D(task.mesh)
        self.log_event('FEM solver initialized', 2)
        
        # SIMP Filter preparation
        self.H, self.sH = self.prepare_filter(task.filter_R)
        self.log_event('Filter prepared', 2)
        
        # Densities initialization
        task.densities = np.ones(self.task.mesh.n_elems) * task.vol_frac
        
        # Translating loads and fixes to FEM solver
        for fix in task.fixed_nodes:
            self.FEM_solver.fix_node(fix[1], fix[0], bool(fix[2]), bool(fix[3]) )
            
        for load in task.applied_loads:
            self.FEM_solver.apply_load(load[1], load[0], load[2], load[3])
        self.log_event('Loads and fixes applied', 2)
        self.log_event('-'*50, 2)
    
    def prepare_filter(self, filter_r):
        H_lines = []
        
        for i in range(self.task.mesh.n_elems):
            neighbors = np.zeros(self.task.mesh.n_elems)
               
            e_row = i % self.task.mesh.ey
            e_col = i // self.task.mesh.ey
            
            min_row = max(0, e_row - math.ceil(filter_r))
            max_row = min(self.task.mesh.ey, e_row + math.ceil(filter_r))
            min_col = max(0, e_col - math.ceil(filter_r))
            max_col = min(self.task.mesh.ex, e_col + math.ceil(filter_r))
            
            for i_row in range(min_row, max_row):
                for i_col in range(min_col, max_col):
                    neighbors[i_col*self.task.mesh.ey + i_row] = max(0, filter_r - 
                                                           np.sqrt((e_col - i_col)**2 + (e_row - i_row)**2))
            
                
            H_lines.append(neighbors)
            
        H = np.stack(H_lines, axis = 0)
        sH = np.sum(H, axis = 1)
        
        return H, sH    
    
    # SIMP Optimization
    def optimize(self, multiprocess_pipe = None):
        # If multiprocess_pipe != None, sends density map to it after each iteration
        self.log_event('Starting optimization', 1)
        iteration = 0
            
        ex = self.FEM_solver.mesh.ex
        ey = self.FEM_solver.mesh.ey
        
        x = np.ones(self.task.mesh.n_elems) * self.task.vol_frac
        xPhys = x
        
        dense_c_norm = 1
        gamma = 1e-3
    
        while (dense_c_norm > self.task.dense_delta):
            iteration += 1
            
            # Matrix assembly with individual densities
            self.FEM_solver.assemble_sparse_K(xPhys, self.task.penalize, self.task.E_void, self.task.E0)
            
            # Displacements
            u = self.FEM_solver.solve_U()
            
            # Compliance, Sensitivity, Filtering
            c = 0
            dc = np.array([])
            dv = np.array([])

            #for e_index, elem in enumerate(self.FEM_solver.elements):
            for e_index in range(self.FEM_solver.mesh.n_elems):
                # Individual compliance
                ce = np.dot(np.dot(u[self.FEM_solver.dofs_matr[e_index]], self.FEM_solver.element_K), u[self.FEM_solver.dofs_matr[e_index]])
                young_modulus = self.task.E_void + pow(xPhys[e_index], self.task.penalize) * (self.task.E0 - self.task.E_void)
    
                c += young_modulus * ce
                curr_dc = -self.task.penalize * (self.task.E0 - self.task.E_void) * pow(xPhys[e_index], self.task.penalize - 1) * ce
    
                dc = np.append(dc, curr_dc)
                dv = np.append(dv, 1)
    
            # Filtering
            for i in range(dc.shape[0]):
                sum_1 = 0
                sum_1 = np.dot(dc * x, self.H[i])
                dc[i] = sum_1 / ((max(gamma, xPhys[i]) * self.sH[i]))
    
            # Optimality criteria
            lambda_1 = 0
            lambda_2 = 1e9
    
            x_new = np.zeros(x.shape)
            while ((lambda_2 - lambda_1) / (lambda_2 + lambda_1)) > 1e-3: #Binary search of lambda
                lambda_mid = (lambda_1 + lambda_2) / 2
    
                for i in range(x.shape[0]):
                    B_e = np.sqrt(-dc[i] / (lambda_mid))
                    if (x[i] * B_e <= max(0, x[i] - self.task.move)):
                        x_new[i] = max(0, x[i] - self.task.move)
                    elif (x[i] * B_e >= min(1, x[i] + self.task.move)):
                        x_new[i] = min(1, x[i] + self.task.move)
                    else:
                        x_new[i] = x[i] * B_e
    
                xPhys = x_new
    
                if (np.sum(xPhys) > self.task.vol_frac * self.FEM_solver.n_elem):
                    lambda_1 = lambda_mid
                else:
                    lambda_2 = lambda_mid
            
            if (iteration == self.task.max_iter):
                break
            
            dense_c_norm = np.max(np.abs(x_new - x))
            x = x_new
            
            
            # Handling multiprocess case: sending progress
            if (multiprocess_pipe != None):
                density_matrix = x.reshape(ex, ey).transpose((1,0))          
                multiprocess_pipe.send(density_matrix)
            
            
            if (iteration % 10  == 1):
                self.log_event(f'Iteration {iteration}, C_norm = {dense_c_norm}', 1)
            self.log_event(f'Iteration {iteration}, C_norm = {dense_c_norm}', 2)
            
            # Updating densities in task
            self.task.densities = x_new
            
        return xPhys        