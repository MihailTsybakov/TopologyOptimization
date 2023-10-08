from matplotlib import pyplot as plt
import numpy as np

# Problem configuration
class Config:
    def __init__(self):
        self.penalize = 3
        self.dense_delta = 0.01
        self.move = 0.2
        
        self.nu = 0.3
        self.E0 = 1
        self.E_void = 1e-9
        self.filter_R = 1.5


# Optimization task specification (Quadrilateral Elements)
class OptimizationTask:
    def __init__(self, mesh, volume_frac, max_iter, config):
        # Common section
        self.mesh = mesh
        self.vol_frac = volume_frac
        self.max_iter = max_iter
        
        # SIMP algorithm section
        self.penalize = config.penalize
        self.dense_delta = config.dense_delta
        self.filter_R = config.filter_R
        self.move = config.move
        
        # Material properties section
        self.nu = config.nu
        self.E0 = config.E0
        self.E_void = config.E_void
        
        # ~FEM section
        self.fixed_nodes = []
        self.applied_loads = []
        
        # Resulting densities (For quadrilateral mesh)
        self.densities = None
    
    # Node fixation for quadrilateral mesh 
    def fix_node(self, node_id_x: int, node_id_y: int, fix_x: bool, fix_y: bool):
        self.fixed_nodes.append([node_id_x, node_id_y, int(fix_x), int(fix_y)])
    
    # Force appliance for quadrilateral mesh
    def apply_load(self, node_id_x: int, node_id_y: int, load_x: float, load_y: float):
        self.applied_loads.append([node_id_x, node_id_y, load_x, load_y])
        
    def save_design(self, save_path):
        ey = self.mesh.ey
        ex = self.mesh.ex
        density_matrix = np.zeros((ey, ex))
        
        for col in range(ex):
            for row in range(ey):
                density_matrix[row][col] = self.densities[col * ey + row]    
        
        np.savetxt(save_path, density_matrix)