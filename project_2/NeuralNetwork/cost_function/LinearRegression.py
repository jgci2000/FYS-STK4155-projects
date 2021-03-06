
import numpy as np
from .CostFunction import CostFunction

class LinearRegression(CostFunction):
    
    def __init__(self, X_train: np.matrix, y_train: np.matrix, X_test: np.matrix, y_test: np.matrix, regularization: float = 0):
        """
            Initiates the LinearRegression class 
            Parameters
                X_train (np.matrix): design train matrix
                y_train (np.matrix): target train values
                X_test (np.matrix): design test matrix
                y_test (np.matrix): target test values
        """
        self.X = X_train
        self.y = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.n = self.y.shape[0]
        self.n_features = self.X.shape[1]
        
        self.reg = regularization
         
    def C(self, beta: np.matrix, indx: np.matrix = np.matrix([])) -> np.matrix:
        """
            Returuns the value of the cost function at a new beta values
            Parameters:
                beta (np.matrix): features vector
        """
        if indx.size == 0:
            return np.mean(np.power((self.X @ beta - self.y), 2)) + self.reg * np.linalg.norm(beta)
        return np.mean(np.power((self.X[indx] @ beta - self.y[indx]), 2)) + self.reg * np.linalg.norm(beta)

    def grad_C(self, beta: np.matrix, indx: np.matrix = np.matrix([])) -> np.matrix:
        """
            Returns the gradient of the function evaluated at a new beta values, 
            using the analytical expression.
            Parameters:
                beta (np.matrix): features vector
        """
        if indx.size == 0:
            return (2 / self.n) * self.X.T @ (self.X @ beta - self.y) + self.reg * beta
        return (2 / self.y[indx].shape[0]) * self.X[indx].T @ (self.X[indx] @ beta - self.y[indx]) + self.reg * beta
    
    def hess_C(self, beta: np.matrix) -> np.matrix:
        """
            Hessian for the cost function
        """
        return self.X.T @ self.X

    def error(self, beta: np.matrix) -> np.matrix:
        """
            Computes the MSE for the test data given the beta values.
            Parameters:
                beta (np.matrix): features vector
        """
        return np.mean((self.y_test - self.X_test @ beta)**2)

    def grad_C_nn(self, y_data: np.matrix, y_tilde: np.matrix) -> np.matrix:
        return (2 / y_tilde.shape[0]) * (y_tilde - y_data)
    
    def error_nn(self, y_data:np.matrix, y_tilde: np.matrix) -> np.matrix:
        """
            Computes the MSE for the test data given the beta values.
            Parameters:
                beta (np.matrix): features vector
        """
        return np.mean(np.multiply(y_data - y_tilde, y_data - y_tilde))
    
    def error_name(self) -> str:
        """
            Returns the string that should be associated with the error_nn values
        """
        return "Error"
    
    def perm_data(self, rng: np.random.Generator):
        """
            Permutes data for SDG
        """
        perm = rng.permuted(np.arange(0, self.n))
        self.X = self.X[perm, :]
        self.y = self.y[perm]  
