import math
import numpy as np
import pyvista as pv
from scipy import sparse
from scipy.sparse.linalg import spsolve

from hex_element import element_K

class FEM_3D():
    def __init__(self, nodes_x, nodes_y, nodes_z, filter_R, nu):
        self.nx = nodes_x
        self.ny = nodes_y
        self.nz = nodes_z
        self.ex = nodes_x - 1
        self.ey = nodes_y - 1
        self.ez = nodes_z - 1
        
        self.n_nodes = nodes_x * nodes_y * nodes_z
        self.n_elems = self.ex * self.ey * self.ez
        
        self.n_dofs = 3 * self.n_nodes
        self.all_dofs = np.arange(self.n_dofs)
        self.fixed_dofs = np.array([], np.int32)
        self.dofs_matrix = np.zeros((self.n_elems, 24), np.int32)
        
        self.K = None
        self.F = np.zeros(self.n_dofs)
        self.U = np.zeros(self.n_dofs)
        
        self.nu = nu
        self.filter_R = filter_R
        
        # Task renderer
        self.plotter = pv.Plotter(lighting = 'three lights')
    
    # Calculates DOFs indexes for element given coords of its pivot node
    def elem_DOFs(self, px, py, pz):
        slice_nodes = self.nx * self.ny
        
        NID_1 = pz*slice_nodes + self.ny * px + (self.ny - py - 1)
        NID_2 = NID_1 + self.ny
        NID_3 = NID_1 + self.ny - 1
        NID_4 = NID_1 - 1
        NID_5 = NID_1 + slice_nodes
        NID_6 = NID_2 + slice_nodes
        NID_7 = NID_3 + slice_nodes
        NID_8 = NID_4 + slice_nodes
        
        node_IDs = [NID_1, NID_2, NID_3, NID_4, NID_5, NID_6, NID_7, NID_8]
        
        elem_dofs = np.zeros(24)
        
        for i in range(8):
            elem_dofs[3*i] = 3*node_IDs[i]
            elem_dofs[3*i + 1] = 3*node_IDs[i] + 1
            elem_dofs[3*i + 2] = 3*node_IDs[i] + 2
            
        return elem_dofs
    
    # Calculates DOFs for each element
    def map_DOFs(self):
        slice_elems = self.ex * self.ey
        for elem_z in range(self.ez):
            for elem_x in range(self.ex):
                for elem_y in range(self.ey):
                    elem_index = slice_elems * elem_z + elem_x*self.ey + (self.ey - elem_y - 1)
                    self.dofs_matrix[elem_index] = self.elem_DOFs(elem_x, elem_y, elem_z)
                    
    def assemble_sparse_K(self, dens, penal, E_void, E0):
        local_K_elems = 24*24
        
        global_iK = np.zeros(local_K_elems * self.n_elems)
        global_jK = np.zeros(local_K_elems * self.n_elems)
        global_vK = np.zeros(local_K_elems * self.n_elems)
        
        for ei in range(self.n_elems):
            elem_density = dens[ei]
            
            young_modulus = E_void + pow(elem_density, penal) * (E0 - E_void)
            KE = element_K(self.nu)*young_modulus
            
            iK = np.kron(self.dofs_matrix[ei], np.ones(24))
            jK = np.reshape(np.kron(self.dofs_matrix[ei], np.reshape(np.ones(24), (24,1))), -1)
            val_K = np.reshape(KE, -1)
            
            global_iK[ei*local_K_elems : (ei+1)*local_K_elems] = iK
            global_jK[ei*local_K_elems : (ei+1)*local_K_elems] = jK
            global_vK[ei*local_K_elems : (ei+1)*local_K_elems] = val_K
        
        self.K = sparse.coo_matrix((global_vK, (global_iK, global_jK)), shape = (self.n_dofs, self.n_dofs)).tocsr()
        
    def solve_U(self):
        free_dofs = np.setdiff1d(self.all_dofs, self.fixed_dofs)
        solution_inv = spsolve(self.K[free_dofs, :][:, free_dofs], self.F[free_dofs])
        self.U[free_dofs] = solution_inv
        
        return self.U
    
    def fix_node(self, node_x, node_y, node_z, fix_x, fix_y, fix_z):
        node_id = (self.nx*self.ny)*node_z + self.ny*node_x + (self.ny - node_y - 1)
        
        dof_x = 3*node_id
        dof_y = 3*node_id + 1
        dof_z = 3*node_id + 2
        
        if (fix_x == True):
            self.fixed_dofs = np.append(self.fixed_dofs, dof_x)
        if (fix_y == True):
            self.fixed_dofs = np.append(self.fixed_dofs, dof_y)
        if (fix_z == True):
            self.fixed_dofs = np.append(self.fixed_dofs, dof_z)
        
        # Marking fixed node
        #self.plotter.add_mesh(pv.Sphere(center = [node_x, node_y, node_z], radius = 0.8), color = 'blue')
            
    def apply_load(self, node_x, node_y, node_z, load_x, load_y, load_z):
        node_id = (self.nx*self.ny)*node_z + self.ny*node_x + (self.ny - node_y - 1)
        
        dof_x = 3*node_id
        dof_y = 3*node_id + 1
        dof_z = 3*node_id + 2
        
        self.F[dof_x] = load_x
        self.F[dof_y] = load_y
        self.F[dof_z] = load_z
        
        # Marking load
        #self.plotter.add_mesh(pv.Cube(center = [node_x, node_y, node_z]), color = 'red')
        
    def save_config(self, densities, path):
        output_file = open(path, 'w')
        
        output_file.write(f'{self.nx} {self.ny} {self.nz}\n')
        output_file.write('section\n')
        
        for i in range(int(self.n_dofs / 3)):
            displ_x = self.U[3*i]
            displ_y = self.U[3*i + 1]
            displ_z = self.U[3*i + 2]
            output_file.write(f'{displ_x} {displ_y} {displ_z}\n')
        output_file.write('section\n')
        
        for i in range(densities.shape[0]):
            output_file.write(f'{densities[i]}\n')
        
        output_file.close()
        
    def render_task(self):
        self.plotter.set_background('#0d1117')
        self.plotter.show_bounds(bounds = [0, self.nx, 0, self.ny, 0, self.nz], color = 'white')
        self.plotter.show()