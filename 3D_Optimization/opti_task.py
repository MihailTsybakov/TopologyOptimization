class OptiTask():
    def __init__(self, nx, ny, nz, nu, config, fixed_nodes, applied_loads, save_path):
        self.config = config
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.fixes = fixed_nodes
        self.loads = applied_loads
        self.nu = nu
        self.save_path = save_path