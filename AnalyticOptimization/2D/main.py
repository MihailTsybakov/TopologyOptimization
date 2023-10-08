from optimize_2d import *
from postprocessor import *

mesh = QuadMesh(60, 40)
config = Config()

task = OptimizationTask(mesh, 0.2, 30, config)

task.fix_node(59, 0, True, True)
task.fix_node(59, 39, True, True)
task.apply_load(0, 10, 0, -1)

optimizer = Optimizer_2D(verbose_level = 2, optimizer_ID = 'ID_0')
optimizer.set_up(task)
densities = optimizer.optimize()

postprocessor = Postprocessor()

save_path = "..\\Data\\Results\\result.txt"
task.save_design(save_path)

postprocessor.load_density_matrix(save_path)
postprocessor.draw_design()
