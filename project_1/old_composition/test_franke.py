
from KFoldSplitter import KFoldSplitter
from Solver import Solver
from FrankeGenerator import FrankeGenerator
from TrainTestSplitter import TrainTestSplitter
from OLSModel import OLSModel
from RidgeModel import RidgeModel
from LassoModel import LassoModel
from ErrDisplayPostProcess import ErrDisplayPostProcess
from PlotPostProcess import PlotPostProcess


solver = Solver(5)

solver.set_data_generator(FrankeGenerator(0, 1, 20, random=True, noise=0.01))

solver.set_splitter(KFoldSplitter())

for i in range(3):
    solver.add_model(LassoModel(0.01 * i))

solver.add_post_process(ErrDisplayPostProcess())
solver.add_post_process(PlotPostProcess())

solver.run()