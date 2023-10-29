# Realization of uniform structured quadrilateral finite element mesh

# Usage: 
# 1. Instantiate QuadMesh object, specifying mesh dimensions along X and Y
# 2. Call map_DOFs() function for DOFs mapping
# 3. Pass QuadMesh object instance to FEM_2D class

import numpy as np

class QuadMesh:
    def __init__(self, nodes_X, nodes_Y):
        self.nx = nodes_X
        self.ny = nodes_Y
        self.ex = nodes_X - 1
        self.ey = nodes_Y - 1
        
        self.n_nodes = nodes_X * nodes_Y
        self.n_elems = self.ex * self.ey
        
        self.n_dofs = nodes_X * nodes_Y * 2                                 # Degrees of freedom
        self.dofs_mapping = np.zeros((self.n_elems, 8), dtype = np.int32)   # What DOFs belong to each element
        
    def map_dofs(self):
        # Calculating DOFs for each element
        
        for i in range(self.ex * self.ey):
            lb_i = self.ny * (i // self.ey) + (i % self.ey) + 1             # Index of left bottom node
            
            elem_dofs = np.array([
                2*lb_i, 2*lb_i + 1,
                2*(lb_i + self.ny), 2*(lb_i + self.ny) + 1,
                2*(lb_i + self.ny - 1), 2*(lb_i + self.ny - 1) + 1,
                2*(lb_i - 1), 2*(lb_i - 1) + 1 ])
            
            self.dofs_mapping[i] = elem_dofs     
            
    def mesh_info(self):
        print(' [Mesh info] ')
        print(f' ------------------')
        print(f' Nodes along X: \t{self.nx}')
        print(f' Nodes along Y: \t{self.ny}')
        print(f' Elems along X: \t{self.ex}')
        print(f' Elems along Y: \t{self.ey}')
        print(f' Total DOFs: \t\t{self.n_dofs}')
        print(f' ------------------')
        print(' Sample DOFs mapping: ')
        
        for i in range(8):
            print(f' Elem {i}: Nodes = {self.dofs_mapping[i]}')
        print(f' ------------------')
         
        