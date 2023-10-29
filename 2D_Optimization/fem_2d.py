# Realisation of a two-dimensional Finite Element Method
# Quadrilateral Elements now supported

import quad_element
from quad_element import QuadElement

import quad_mesh
from quad_mesh import QuadMesh

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

class FEM_2D():
    def __init__(self, mesh: QuadMesh):
        
        self.mesh = mesh                                              # Finite Element Mesh
        self.n_elem = mesh.n_elems
        
        self.all_dofs = np.arange(0, mesh.n_dofs)                     # List containing DOFs indicies
        self.fixed_dofs = np.array([], np.int32)                      # List containing indicies of fixed DOFs
        self.dofs_matr = mesh.dofs_mapping
        
        self.K = None                                                 # Global Stiffness Matrix
        self.F = np.zeros(mesh.n_dofs)                                # Loads vector, size = number of DOFs
        self.U = np.zeros(mesh.n_dofs)                                # Displacements, size = number of DOFs
        
        self.canv = np.ones((mesh.ny, mesh.nx))                       # Empty canvas for marking boundary conds & loads
        
        self.nu = 0.3                                                 # Poisson Ratio
        self.element_K = quad_element.quad_elem_instance.local_K      # Local stiffness matrix for quad element
            
    def assemble_sparse_K(self, dens, penal, E_void, E0):
        
        global_iK = np.zeros(64 * self.n_elem)
        global_jK = np.zeros(64 * self.n_elem)
        global_vK = np.zeros(64 * self.n_elem)
        
        for ei in range(self.dofs_matr.shape[0]):
            elem_density = dens[ei]
            
            young_modulus = E_void + pow(elem_density, penal) * (E0 - E_void)
            KE = self.element_K * young_modulus
            
            iK = np.kron(self.dofs_matr[ei], np.ones(8))
            jK = np.reshape(np.kron(self.dofs_matr[ei], np.reshape(np.ones(8), (8,1))), -1)
            val_K = np.reshape(KE, -1)
            
            global_iK[ei*64 : (ei+1)*64] = iK
            global_jK[ei*64 : (ei+1)*64] = jK
            global_vK[ei*64 : (ei+1)*64] = val_K
            
        self.sparse_K = sparse.coo_matrix((global_vK, (global_iK, global_jK)), 
                                          shape = (self.mesh.n_dofs, self.mesh.n_dofs)).tocsr()
        
    def solve_U(self):
        free_dofs = np.setdiff1d(self.all_dofs, self.fixed_dofs)
        self.U[free_dofs] = spsolve(self.sparse_K[free_dofs, :][:, free_dofs], self.F[free_dofs])
        
        return self.U
            
    # Fix node (=dofs) in [row, col] position 
    def fix_node(self, row, col, fix_x, fix_y):
        node_ind = self.mesh.ny * col + row
        
        dof_x = node_ind * 2
        dof_y = node_ind * 2 + 1
        
        if (fix_x == True):
            self.fixed_dofs = np.append(self.fixed_dofs, dof_x)
            
        if (fix_y == True):
            self.fixed_dofs = np.append(self.fixed_dofs, dof_y)
            
        self.mark_node(row, col, -3.0)
    
    # Fix nodes (=dofs) in whole row
    def fix_row(self, row, fix_x, fix_y):
        for col in range(self.mesh.nx):
            self.fix_node(row, col, fix_x, fix_y)
    
    # Fix nodes (=dofs) in whole column
    def fix_col(self, col, fix_x, fix_y):
        for row in range(self.mesh.ny):
            self.fix_node(row, col, fix_x, fix_y)
    
    # Adds (Fx, Fy) load to [row, col] node 
    def apply_load(self, row, col, Fx, Fy):
        node_ind = self.mesh.ny * col + row
        
        dof_x = node_ind * 2
        dof_y = node_ind * 2 + 1
        
        self.F[dof_x] = Fx
        self.F[dof_y] = Fy
        
        self.mark_node(row, col, 3.0)
        
    def draw_marked(self):
        plt.imshow(self.canv, cmap = 'gist_earth')
        
    def mark_node(self, row, col, val):
        for i_row in range(row - 2, row + 3):
            for i_col in range(col - 2, col + 3):
                if (i_row >= 0 and i_col >= 0 and i_row < self.mesh.ny and i_col < self.mesh.nx):
                    self.canv[i_row, i_col] = val
        self.canv[row, col] = 0
    
    def save_txt(self, filename, densities):
        outfile = open(filename, 'w')
        
        outfile.write(f'{self.mesh.nx} {self.mesh.ny}\n')
        outfile.write('-section-\n')
        
        for di in range(self.U.shape[0]):
            outfile.write(f'{self.U[di]}\n')
        outfile.write('-section-\n')
        
        for fd in range(self.fixed_dofs.shape[0]):
            outfile.write(f'{self.fixed_dofs[fd]}\n')
            
        outfile.write('-section-\n')
        for d_i in range(densities.shape[0]):
            outfile.write(f'{densities[d_i]}\n')
            
        outfile.close()
        