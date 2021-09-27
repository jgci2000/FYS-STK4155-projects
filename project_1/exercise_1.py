
import numpy as np
import matplotlib.pyplot as plt

from Solver import Solver
from OLSModel import OLSModel
from FrankeGenerator import FrankeGenerator
from TrainTestSplitter import TrainTestSplitter
from PlotPostProcess import PlotPostProcess
from ErrDisplayPostProcess import ErrDisplayPostProcess
from StandardScaler import StandardScaler

degree = 5
solver = Solver(degree=degree, fit_intercept=False)

solver.set_data_generator(FrankeGenerator(0, 1, 50, random=True, noise=0.1))
solver.set_splitter(TrainTestSplitter())
solver.add_model(OLSModel())

solver.add_post_process(ErrDisplayPostProcess())
solver.add_post_process(PlotPostProcess())
solver.run()

solver.set_scaler(StandardScaler(with_std=False))
solver.run()