# Realization of linear quadrilateral finite element
# Singleton template: one element gives stiffness matrix for all needs

import numpy as np

class QuadElement:
    def __init__(self, poisson_ratio):
        self.nu = poisson_ratio
        
        # Local stiffness matrix assembly
        A11 = np.transpose(np.array([
            [12, 3, -6, -3],
            [3, 12, 3, 0],
            [-6, 3, 12, -3],
            [-3, 0, -3, 12]
        ]))
        
        A12 = np.array([
            [-6, -3, 0, 3],
            [-3, -6, -3, -6],
            [0, -3, -6, 3],
            [3, -6, 3, -6]
        ])
        
        B11 = np.transpose(np.array([
            [-4, 3, -2, 9],
            [3, -4, -9, 4],
            [-2, -9, -4, -3],
            [9, 4, -3, -4]
        ]))
        
        B12 = np.array([
            [2, -3, 4, -9],
            [-3, 2, 9, -2],
            [4, 9, 2, 3],
            [-9, -2 , 3, 2]
        ])
        
        block_1 = np.concatenate((np.concatenate((A11, A12), axis = 1), 
                                  np.concatenate((np.transpose(A12), A11), axis = 1)), axis = 0)
        block_2 = np.concatenate((np.concatenate((B11, B12), axis = 1), 
                                  np.concatenate((np.transpose(B12), B11), axis = 1)), axis = 0)
        
        self.local_K = (block_1 +  self.nu*block_2)/ (1 - pow(self.nu, 2)) / 24        
        

# Instantiating element

quad_elem_instance = QuadElement(0.3)