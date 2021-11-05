
import numpy as np
from time import time
from typing import Callable

from .Layer import Layer, HiddenLayer, OutputLayer
from .cost_function.CostFunction import CostFunction

from sklearn.model_selection import train_test_split


class Model:
    """
        Feed-forward neural network instance
        Can add layers to the network with add_layer
    """
    
    def __init__(self, input_size: int, cost_function: CostFunction, random_state: int = int(time())):
        """
            Artificial neural network class
            Parameters:
                input_size (int): Size of the input layer (i.e. number of features), which will determine the number of weights in the first hidden layer
                random_state (int): Seed value to use for RNG
        """

        self._input_size = input_size

        self.random_state = random_state
        self.rng = np.random.default_rng(np.random.MT19937(seed=self.random_state))
        
        self.layers = list()
        self.cost_function = cost_function
        self._has_output = False
        
    

    def add_layer(self, layer: Layer):
        """
            Adds a layer to the Model class.
            It has to have at least one OutputLayer.
            The layers must be added by the order they act.
        """

        # Ensure no more than 1 output layer
        if self._has_output:
            print('\033[91mCannot add another layer after the network\'s output layer! Make sure layers are being added in the correct order.\033[0m')
            return

        # Compute number of inputs the layer will be receiving to init weights
        n_inputs = self._input_size
        if len(self.layers) > 0:
            n_inputs = self.layers[-1].get_size()
        layer.init_weights(n_inputs, self.rng)
        
        # Add layer
        self.layers.append(layer)
        if isinstance(layer, OutputLayer):
            self._has_output = True # Locks the layers array to prevent adding more after the output layer

    def is_ready(self) -> bool:
        """
            Helper to determine whether the ANN is ready for training
            Returns:
                (bool): Whether the network is ready, i.e. has been given all its layers
        """
        return self._has_output

    def feed_forward(self, inputs: np.matrix, training: bool = False) -> tuple:
        """
            Runs through the network once with a given list of inputs and returns the obtained outputs
            Parameters:
                inputs (np.matrix|list<float>): The set of inputs to give to the network
                training (bool): If true, will return hidden layer activations alongside the actual outputs
            Returns:
                (np.matrix|list<float>): Outputs obtained out of the output layer after running through all layers, returned only if `training` was `false`
                (list<np.matrix>): Hidden layer activated outputs, returned only if `training` was `true`
                (list<np.matrix>): Hidden layer outputs (no activation function), returned only if `training` was `true`
        """

        # If the input is given as a 1D array, we're wanting to use that as a single row in the input matrix (i.e. run with a single set of input data)
        output_list = False
        if isinstance(inputs, list):
            inputs = np.matrix([inputs])
            output_list = True
        
        if inputs.ndim == 1:
            inputs = np.matrix(inputs)

        if not self.is_ready():
            print('\033[91mNetwork hasn\'t been given an output layer! Make sure the neural network is set-up with all layers before starting training\033[0m')
            return

        if inputs.shape[1] != self._input_size:
            print('\033[91mCannot feed input of size', inputs.shape, 'into ANN with input size', self._input_size, '.\033[0m')
            return

        # Process from layer to layer sequentially, passing the output of each layer into the next
        tmp = inputs
        if training:
            a_h = [inputs]
            z_h = [inputs]
        for layer in self.layers:

            # Activate the layer
            tmp, z = layer.forward(tmp)

            # If for whatever reason some kind of error occured, the output of forward() will be null
            if tmp is None:
                print('\033[91mLayer gave invalid results; see above for details regarding the error.\033[0m')
                return None
            
            # In training, keep track of hidden layer outputs
            if training:
                z_h.append(z)
                a_h.append(tmp)
        
        # Output of final layer = output of network
        if output_list:
            tmp = tmp[0] # Output as a list if the input was given as such
        if training:
            return a_h, z_h
        return tmp

    def error(self, inputs: np.matrix, targets: np.matrix) -> float:
        """
            Feeds forward once, then returns the mean squared error between targets and outputs
            Parameters:
                inputs (np.matrix): Inputs to run the network on
                targets (np.matrix): Expected outputs
            Returns:
                (float): Mean squared error after prediction
        """
        return self.cost_function.error_nn(targets, self.feed_forward(inputs))


    def back_prop(self, inputs: np.matrix, targets: np.matrix, learning_rate: float = 0.1, regularization: float = 0):
        """
            Back-propagates once with a set of actual and desired outputs, so the next run will match the targets closer (hopefully)
            Parameters:
                inputs (np.matrix): Inputs to train for
                targets (np.matrix): Desired outcome values
                learning_rate (float): Learning rate η to use to update the weights & biases
                regularization (float): Regularization parameter λ to control rate of descent
        """

        if not self.is_ready():
            print('\033[91mNetwork hasn\'t been given an output layer! Make sure the neural network is set-up with all layers before starting training\033[0m')
            return

        # Iterate over list of inputs/targets if passing more than 1
        for i in range(inputs.shape[0]):
            ins = inputs[i]
            targs = targets[i]

            # Feed forward once to obtain outputs
            a_h, z_h = self.feed_forward(ins, training=True)

            # Dimensionality check
            if a_h[-1].shape != targs.shape or a_h[-1].shape[1] != self.layers[len(self.layers) - 1].get_size():
                print('\033[91mMismatching outputs/targets size; should be (x,', self.layers[len(self.layers) - 1].get_size(), '), got', a_h[-1].shape, 'and', targs.shape, 'instead..\033[0m')
                return
            
            # Compute errors & gradient descent for each layer
            # Going backwards from last to first layer
            prev_layer_err = np.multiply(self.cost_function.grad_C_nn(targs, a_h[-1]), self.layers[-1]._activation_fn.d(z_h[-1]))
            for j in range(len(self.layers)-1, -1, -1): # for (let i = len(self.layers) - 1; i >= 0; --i)       (python is fucking garbage)
                # Update layer
                prev_layer_err = self.layers[j].backward(a_h[j], z_h[j], prev_layer_err, learning_rate, regularization)
    

    def train(self, inputs: np.matrix, targets: np.matrix, epochs: int = 1000, learning_rate: float = 0.1, regularization: float = 0, verbose: bool = True):
        """
            Back-propagates over a series of epochs with a given learning rate and regularization hyperparameter
            Parameters:
                inputs (np.matrix): Inputs to train for
                targets (np.matrix): Desired outcome values
                epochs (int): Number of training epochs to train over
                learning_rate (float): Learning rate η to use to update the weights & biases
                regularization (float): Regularization parameter λ to control rate of descent
                verbose (bool): Whether to output the completion percentage to stdout
        """

        if not self.is_ready():
            print('\033[91mNetwork hasn\'t been given an output layer! Make sure the neural network is set-up with all layers before starting training\033[0m')
            return
        
        for epoch in range(1, epochs + 1):

            if verbose:
                print(f"[ Epoch: {epoch}/{epochs}; Error: {self.cost_function.error_nn(self.feed_forward(inputs), targets)} ]")

            self.back_prop(inputs, targets, learning_rate=learning_rate, regularization=regularization)

        print()
        print(f"[ Finished training with error: {self.cost_function.error_nn(self.feed_forward(inputs), targets)} ]")

    def train_sgd(self, inputs: np.matrix, targets: np.matrix, learning_rate: float, epochs: int = 1000, minibatch_size: int = 5, regularization: float = 0, verbose: bool = True):
        """
            Back-propagates over a series of epochs using stochastic gradient descent
            Parameters:
                inputs (np.matrix): Inputs to train for
                targets (np.matrix): Desired outcome values
                learning_rate (function): learning_rate
                epochs (int): Number of training epochs to train over
                minibatch_size (int): Size of individual mini-batches
                regularization (float): Regularization parameter λ to control rate of descent
                verbose (bool): Whether to output the completion percentage to stdout
        """

        if not self.is_ready():
            print('\033[91mNetwork hasn\'t been given an output layer! Make sure the neural network is set-up with all layers before starting training\033[0m')
            return

        # number of mini-batches
        minibatch_count = int(inputs.shape[0] / minibatch_size)

        for epoch in range(1, epochs + 1):
            
            # Permute data each epoch
            perm = self.rng.permuted(np.arange(0, inputs.shape[0]))
            inputs = inputs[perm, :]
            targets = targets[perm, :]

            # Go through all minibatches in the input set
            for m in range(minibatch_count):
                idx = minibatch_size * int(self.rng.random() * minibatch_count)
                ins = inputs[idx : idx + minibatch_size]
                targs = targets[idx : idx + minibatch_size]
                
                self.back_prop(ins, targs, learning_rate=learning_rate, regularization=regularization)
            
            if verbose:
                print(f"[ Epoch: {epoch}/{epochs}; Error: {self.cost_function.error_nn(self.feed_forward(inputs), targets)} ]")

        print()
        print(f"[ Finished training with error: {self.cost_function.error_nn(self.feed_forward(inputs), targets)} ]")
    
    def train_sgd_validation(self, inputs: np.matrix, targets: np.matrix, learning_rate: float, validation_set_size: float = 0.2, epochs: int = 1000, minibatch_size: int = 5, regularization: float = 0, epsilon: float = 0.025, verbose: bool = True) -> int:
        """
            Back-propagates over a series of epochs using stochastic gradient descent
            Parameters:
                inputs (np.matrix): Inputs to train for
                targets (np.matrix): Desired outcome values
                learning_rate (float): learning_rate 
                validation_set_size (float): Size of the validation set to use to stop training early
                epochs (int): Number of training epochs to train over
                minibatch_size (int): Size of individual mini-batches
                regularization (float): Regularization parameter λ to control rate of descent
                epsilon (float): Allowed value by which the MSE can increase without exiting early
                verbose (bool): Whether to output the completion percentage to stdout
            Returns:
                (int): Number of epochs after which the training stopped; which may be an early-out once the MSE starts going up
        """

        if not self.is_ready():
            print('\033[91mNetwork hasn\'t been given an output layer! Make sure the neural network is set-up with all layers before starting training\033[0m')
            return
        
        # split into training and validation sets
        perm = self.rng.permuted(np.arange(0, inputs.shape[0]))
        inputs = inputs[perm, :]
        targets = targets[perm, :]
        inputs, in_validation, targets, out_validation = train_test_split(inputs, targets, test_size=validation_set_size)

        # number of mini-batches
        minibatch_count = int(inputs.shape[0] / minibatch_size)

        prev_mse = None
        for epoch in range(1, epochs + 1):

            # Permute data each epoch
            perm = self.rng.permuted(np.arange(0, inputs.shape[0]))
            inputs = inputs[perm, :]
            targets = targets[perm, :]
            
            # Go through all minibatches in the input set
            for m in range(minibatch_count):
                idx = minibatch_size * int(self.rng.random() * minibatch_count)
                ins = inputs[idx : idx + minibatch_size]
                targs = targets[idx : idx + minibatch_size]

                self.back_prop(ins, targs, learning_rate=learning_rate, regularization=regularization)

            # Get validation set error
            pred = self.feed_forward(in_validation)
            mse = self.cost_function.error_nn(pred, out_validation)
            if prev_mse is not None and mse - prev_mse > prev_mse + epsilon:
                break # Stop early
            prev_mse = mse
            
            if verbose:
                print(f"[ Epoch: {epoch}/{epochs}; Error: {self.cost_function.error_nn(self.feed_forward(in_validation), out_validation)} ]")

        print()
        print(f"[ Finished training with error: {self.cost_function.error_nn(pred, out_validation)} ]")
        
        return epoch+1 # Return the actual number of epochs obtained
    
