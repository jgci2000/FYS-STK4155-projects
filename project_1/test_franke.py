
from Solver import Solver
from FrankeGenerator import FrankeGenerator
from TrainTestSplitter import TrainTestSplitter
from OLSModel import OLSModel
from OLSSVDModel import OLSSVDModel
from ErrDisplayPostProcess import ErrDisplayPostProcess
from PlotPostProcess import PlotPostProcess


solver = Solver(5)

generator = FrankeGenerator(0, 1, 0.01, noise=0.01)
solver.set_data_generator(generator)

solver.set_splitter(TrainTestSplitter())

solver.set_model(OLSSVDModel())

solver.add_post_process(ErrDisplayPostProcess())
solver.add_post_process(PlotPostProcess())

solver.run()
