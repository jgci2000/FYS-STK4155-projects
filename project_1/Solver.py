
import numpy as np
from DataGenerator import DataGenerator
from Splitter import Splitter
from Model import Model
from PostProcess import PostProcess
from Scaler import Scaler
import copy

class Solver:
    """
        Component-based solver implementation
        Components can be added to a solver instance to set up a model, a data generator, a scaler, etc.
    """


    def __init__(self, degree: int, fit_intercept: bool = False, data_generator: DataGenerator = None, splitter: Splitter = None, scaler: Scaler = None, models = list(), post_processes = list(), seed: int = 0):
        """
            Default Solver constructor
            Parameters can be used to set up components on the Solver in a non-verbose way
        """
        self._degree = degree
        self._fit_intercept = fit_intercept
        self._data_generator = data_generator
        self._splitter = splitter
        self._models = copy.deepcopy(models)
        self._post_processes = copy.deepcopy(post_processes)
        self._rng = np.random.default_rng(np.random.MT19937(seed))
        self._scaler = scaler

        # Generate the data
        if self._data_generator != None:
            self._data = self._data_generator.generate(self._rng) 
    
    def set_data_generator(self, data_generator: DataGenerator):
        """
            Sets the data generator on the solver instance
            Parameters:
                data_generator (DataGenerator): The data generator to use
        """
        self._data_generator = data_generator
        
        # Generate the data
        self._data = self._data_generator.generate(self._rng)

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data
    
    def set_splitter(self, splitter: Splitter):
        """
            Sets the splitter on the solver instance
            Parameters:
                splitter (Splitter): The splitter to use
        """
        self._splitter = splitter
    
    def add_model(self, model: Model):
        """
            Sets the model on the solver instance
            Parameters:
                model (Model): The model to use to predict the data
        """
        self._models.append(model)
        
    def set_scaler(self, scaler: Scaler):
        """
            Sets the scaler on the solver instance
            Parameters:
                scaler (Scaler): The scaler to use to scale the data
        """
        self._scaler = scaler

    def add_post_process(self, post_process: PostProcess):
        """
            Adds a post-process pass to the solver instance
            Parameters:
                post_process (PostProcess): The post process pass to append and run once predictions are made
        """
        self._post_processes.append(post_process)

    def _design_matrix(self, x1: np.matrix, x2: np.matrix) -> np.matrix:
        """
            Create the design matrix in the form of a Vandermonde matrix for one or two
            dimensional data set. The matrix is of the form

            [[1 x_1 x_1^2 ... x_1^(degree)]
             ...
             [1 x_n x_n^2 ... x_n^(degree)]]

            in 1D, and

            [[1 x_1 y_1 x_1^2 x_1y_1 y_1^2 ... y_1^(degree)]
             ...
             [1 x_n y_n x_n^2 x_ny_n y_n^2 ... y_n^(degree)]]

            in 2D.
            
            Parameters: 
                x1 (numpy array): The input data points on the X axis
                x2 (numpy array): The input data points on the Y axis, or None if generating 1D set
            
            Returns: 
                (numpy array): (n x p) dimensional matrix, 
                where n is number of datapoints and p is the degree 
                plus 1 (1-variable input) or p = degree*(degree + 1)/2 (2-variable input)
        """

        if x2 is None: # 1-variable Vandermonde matrix
            X = np.ones((len(x1), self._degree + 1)) # First column of design matrix is 1

            for i in range(1, self._degree+1): # First column is 1, so we skip it
                X[:, i] = x1.T ** i
        
        else: # 2-variable Vandermonde matrix
            X = np.ones((len(x1), int((self._degree + 1) * (self._degree + 2) / 2))) # First column of design matrix is 1
            # The number of features are 1 + 2 + ... + (degree+1) = (degree+1)*(degree+2)/2
            for i in range(1, self._degree + 1): # First column is 1, so we skip it
                q = int(i * (i + 1) / 2) # 1 + 2 + ... + i
                for k in range(i + 1):
                    X[:, q + k] = (x1[:, 0] ** (i - k)) * (x2[:, 0] ** k)
        
        # Return design matrix
        return X


    def run(self):
        """
            Runs the data generator, model, and other attached components to create necessary prediction(s)
        """
        
        # Check setup
        if self._data_generator == None:
            print('Error: no data generator has been defined on the solver!')
            return
        if len(self._models) <= 0:
            print('Error: no model has been defined on the solver!')
            return
        
        # Create design matrix
        X_full = self._design_matrix(self._data[0], self._data[1] if len(self._data) > 2 else None)

        # Split data optionally
        if self._splitter != None:
            X_split, y_split = self._splitter.split(X_full, self._data[-1])
        else:
            X_split = { 'full': X_full }
            y_split = { 'full': self._data[-1] }
        
        # Scale data optionally
        if self._scaler != None and len(X_split.keys()) > 1:
            self._scaler.prepare(X_split['train']) 
            for key in list(X_split.keys()):
                new_key = key + '_scaled'
                X_split[new_key] = self._scaler.scale(X_split[key])
                
            self._scaler.prepare(y_split['train'])
            for key in list(y_split.keys()):
                new_key = key + '_scaled'
                y_split[new_key] = self._scaler.scale(y_split[key])
        
        if not self._fit_intercept: 
            for key in X_split.keys():
                X_split[key][:, 0] = 0
        
        # Init model and get evaluator to make predictions out of
        # Selecting which set to use out of the full set depending on the labeled sets in X_split and y_split
        if 'train_scaled' in X_split.keys():
            X = X_split['train_scaled']
            y = y_split['train_scaled']
        elif 'train' in X_split.keys():
            X = X_split['train']
            y = y_split['train']
        else:
            X = X_split['full']
            y = y_split['full']

        # Compute beta values for all models
        betas = {}
        for model in self._models:
            betas[model.name] = model.interpolate(X, y)
        
        # Make predictions for all models and all subsets
        predictions = {}
        
        if 'train_scaled' in X_split.keys():
            for model in self._models:
                predictions[model.name] = {}
                for key in X_split.keys():
                    if 'scaled' in key:
                        predictions[model.name][key] = X_split[key] @ betas[model.name] 
        else:
            for model in self._models:
                predictions[model.name] = {}
                for key in X_split.keys():
                    predictions[model.name][key] = X_split[key] @ betas[model.name]
        
        # Run post-processes on original data + full prediction
        for process in self._post_processes:
            process.run(self._data, X_split, y_split, predictions, betas, self._degree)
