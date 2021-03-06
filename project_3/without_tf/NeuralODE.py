import autograd.numpy as np
from autograd import grad, elementwise_grad
from time import time
from typing import Callable, List

class NeuralODE():
    """
        Neural ODE Class
    """    
    
    def __init__(self, n_input_nodes: int, random_state: int = int(time())):
        """
            Initiates Neural Network. 
            The number of input nodes has to be the number of features. Then an array can be passed contaning all of the datapoints for that feature.
            Parameters:
                n_input_nodes (int): number of input nodes
                random_state (int): seed for rng
        """
        self.random_state = random_state
        self.rng = np.random.default_rng(np.random.MT19937(seed=random_state))

        self.params = list()
        self.activation_function = list()
        self.n_layers = 0
        self.n_input_nodes = n_input_nodes
        
    def add_layer(self, n_nodes: int, activation_function: Callable, bias_init: float = 1e-6):
        """
            Adds a layer to the NeuralNetwork.
            Parameters:
                n_nodes (int): number of nodes for the given layer
                activation_function (Callable): Callable object 
                bias_init (float): constant for initialization of bias vector
        """
        if self.n_layers == 0:
            weights = self.rng.normal(0, 1, size=(n_nodes, self.n_input_nodes))
            biases = self.rng.uniform(0, 1, size=(n_nodes, 1)) * bias_init
            
            self.params.append(np.zeros((n_nodes, 1 + self.n_input_nodes)))
            self.params[-1][:, 0:1] = biases
            self.params[-1][:, 1:] = weights
            self.activation_function.append(activation_function)
        else: 
            weights = self.rng.normal(0, 1, size=(n_nodes, self.params[-1].shape[0]))
            biases = self.rng.uniform(0, 1, size=(n_nodes, 1)) * bias_init
            
            self.params.append(np.zeros((n_nodes, 1 + self.params[-1].shape[0])))
            self.params[-1][:, 0:1] = biases
            self.params[-1][:, 1:] = weights
            self.activation_function.append(activation_function)
        
        self.n_layers += 1
        
    def feed_forward(self):
        """
            Return the feed forward function for the Neural Network.
        """
        activ_funcs = self.activation_function
        
        def ff(x, params):
            n = np.max(x.shape)
            a_l = x.reshape(-1, n)
            
            for l in range(len(params)):
                a_l = activ_funcs[l](np.matmul(params[l], np.concatenate((np.ones((1, n)), a_l), axis=0)))
            
            return a_l
        
        return ff
    
    def set_trial(self, trial: Callable):
        """
            Sets the trial function.
            Parameters: 
                trial (Callable): trial function.
        """
        self.trial = trial
    
    def set_ode(self, ode: Callable): 
        """
            Sets the ODE to solve. Sets the right side of the equation
            Parameters: 
                ode (Callable): ode function.
        """
        self.right = ode
    
    def set_left(self, left: Callable):
        """
            Sets the left side of the equation.
            Parameters:
                left (Callable): left side of the equation.
        """
        self.left = left

    def cost_function(self):
        """
            Returns the cost function for the Neural Network to optimize.
        """
        return lambda x, params: np.mean((self.left(x, params) - self.right(x, params))**2)

    def train(self, x: np.ndarray, epochs: int, learning_rate: Callable):
        """
            Training function for the NeuralNetwork. Trains the weights and biases with Gradient Descent.
            Parameters:
                x (np.ndarray): inputs to the NeuralNetwork.
                epochs (int): epochs for the training process.
                leraning_rate (Callable): learning rate for the GD method. Can be a function of the epochs.
        """
        grad_C = grad(self.cost_function(), 1)
        
        for epoch in range(1, epochs + 1):
            
            grad_C_params = grad_C(x, self.params)

            for l in range(self.n_layers):
                self.params[l] = self.params[l] - learning_rate(epoch) * grad_C_params[l]
                    
            print(f" [ epoch: {epoch}/{epochs} ] ", end='\r')
                    
    def compute_solution(self, x: np.ndarray):
        """
            Computes the solution for the given points. 
            Parameters:
                x (np.ndarray): points to compute the solution on.
        """
        return self.trial(x, self.params)[0]

if __name__ == '__main__':
    from Activation import sigmoid, linear
    import matplotlib.pyplot as plt
    
    def forward_euler(x, f0, g_euler):
        n = np.size(x)
        h = (x[-1] - x[0]) / n
        
        solution = np.zeros(n)
        solution[0] = f0
        
        for i in range(0, n - 1):
            solution[i + 1] = solution[i] + h * g_euler(solution[i])
            
        return solution
    
    print("Testing NeuralODE code! ")
    
    seed = 1337
    
    N = 100
    x = np.linspace(0, 1, N)
    
    nn = NeuralODE(1, random_state=seed)
    nn.add_layer(50, sigmoid())
    nn.add_layer(1, linear())
    
    ff = nn.feed_forward()
    
    # Exponential Decay
    alpha = 2
    A = 1
    f0 = 1.2
    euler = lambda x: alpha * x * (A - x)
    trial = lambda x, params: f0 + x * ff(x, params)
    ode = lambda x, params: alpha * trial(x, params) * (A - trial(x, params))
    left = lambda x, params: elementwise_grad(trial, 0)(x, params) 
    analytical = lambda x: A * f0 / (f0 + (A - f0) * np.exp(- alpha * A * x))
    
    # Harmonic Approxilator test
    # f0 = 1
    # w0 = 2
    # trial = lambda x, params: w0 * np.sin(x) + x**2 * ff(x, params)
    # left = lambda x, params: elementwise_grad(elementwise_grad(trial, 0), 0)(x, params)
    # ode = lambda x, params: w0**2 * trial(x, params)
    # analytical = lambda x: np.sin(w0 * x)
        
    # 1D Poisson equatino
    # f0 = 0
    # f1 = 1
    # trial = lambda x, params: x * (1 - x) * ff(x, params)
    # left = lambda x, params: elementwise_grad(elementwise_grad(trial, 0), 0)(x, params)
    # ode = lambda x, params: - (3 * x + x**2) * np.exp(x)
    # analytical = lambda x: x * (1 - x) * np.exp(x)
    
    nn.set_trial(trial)
    nn.set_ode(ode)
    nn.set_left(left)
    eta = lambda x: 1e-4
    nn.train(x, 5000, learning_rate=eta)
    
    nn_sol = nn.compute_solution(x)
    
    plt.figure(1)
    plt.plot(x, nn_sol, label="NeuralODE")
    plt.plot(x, forward_euler(x, f0, euler), label="Forward Euler")
    plt.plot(x, analytical(x), label="Analytic")
    plt.xlabel(r"$x$")
    plt.ylabel(r"$f(x)$")
    plt.legend()
    plt.show()
    
   
 