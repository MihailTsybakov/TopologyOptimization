from optimize_3d import*
from problem_config import *

# Problem configuration
config = Config()

nx = 30
ny = 30
nz = 30

config.nx = nx
config.ny = ny
config.nz = nz

config.vol_frac = 0.07
config.penalize = 3
config.dense_delta = 0.01
config.move = 0.2
config.filter_R = 1.5
config.E_void = 1e-9
config.E0 = 1
config.max_iter = 12
config.save_iters = [1, 2, 5, 10, 15, 20]
config.save_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data'

nu = 0.3

# Finite Element Method solver initialization
FEM_solver = FEM_3D(nx, ny, nz, config.filter_R, nu)

# Loads & Boundary conditions
FEM_solver.fix_node(3, 29, 3, True, True, True)
FEM_solver.fix_node(3, 29, 27, True, True, True)
FEM_solver.fix_node(27, 29, 3, True, True, True)
FEM_solver.fix_node(27, 29, 27, True, True, True)

#print('Applying load')
FEM_solver.apply_load(14, 0, 24, 0, -1, -1)
FEM_solver.apply_load(15, 0, 24, 0, -1, -1)
    
print(f'Problem formulated. Finite elements: {FEM_solver.n_elems}')

#FEM_solver.render_task()
# Setup
print(f'Mapping Degrees of freedom')
FEM_solver.map_DOFs() 
print('DOFs mapped')

print(f'Optimizing in {FEM_solver.ex}x{FEM_solver.ey}x{FEM_solver.ez} domain...', flush = True)
xPhys_optimized = optimize_3D(FEM_solver, config, True, False)

path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data\\New1.txt'
FEM_solver.save_config(xPhys_optimized, path)