# Settings for optimization problem

class Config():
    def __init__(self):
        self.vol_frac = 0.0
        self.penalize = 0
        self.move = 0 
        self.dense_delta = 0.0
        self.max_iter = 0
        self.E_void = 0
        self.E0 = 0
        self.H = None
        self.sH = None
        self.fem_save_iters = None