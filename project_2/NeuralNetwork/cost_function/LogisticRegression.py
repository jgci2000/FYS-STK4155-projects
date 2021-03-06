
import re
import numpy as np

from .CostFunction import CostFunction

class LogisticRegression(CostFunction):
    
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
        self.sigmoid = lambda z: 1 / (1 + np.exp(- z))
        
        self.reg = regularization
         
    def C(self, beta: np.matrix, indx: np.matrix = np.matrix([])) -> np.matrix:
        """
            Returuns the value of the cost function at a new beta values
            Parameters:
                beta (np.matrix): features vector
        """
        if indx.size == 0:
            z = self.X @ beta
            return - np.mean(- self.y * np.log(self.sigmoid(z)) - (1 - self.y) * np.log(self.sigmoid(1 - z))) + self.reg * np.linalg.norm(beta)
        z = self.X[indx] @ beta
        return - np.mean(- self.y[indx] * np.log(self.sigmoid(z)) - (1 - self.y[indx]) * np.log(self.sigmoid(1 - z))) + self.reg * np.linalg.norm(beta)

    def grad_C(self, beta: np.matrix, indx: np.matrix = np.matrix([])) -> np.matrix:
        """
            Returns the gradient of the function evaluated at a new beta values, 
            using the analytical expression.
            Parameters:
                beta (np.matrix): features vector
        """
        if indx.size == 0:
            z = self.X @ beta
            return - (self.X.T @ (self.y - self.sigmoid(z))) / self.n + self.reg * beta
        z = self.X[indx] @ beta
        return - (self.X[indx].T @ (self.y[indx] - self.sigmoid(z))) / self.y[indx].shape[0] + self.reg * beta
    
    def hess_C(self, beta: np.matrix) -> np.matrix:
        """
            Hessian for the cost function
        """
        z = self.X @ beta
        W = np.diag( (self.sigmoid(z)*(1-self.sigmoid(z))).reshape(-1) )
        return self.X.T @ W @ self.X

    def error(self, beta: np.matrix) -> np.matrix:
        return np.sum((self.sigmoid(self.X_test @ beta)).round() == self.y_test) / self.y_test.shape[0]

    def grad_C_nn(self, y_data: np.matrix, y_tilde: np.matrix) -> np.matrix:
        return - (y_data - y_tilde) / y_tilde.shape[0]
    
    def error_nn(self, y_data: np.matrix, y_tilde: np.matrix) -> np.matrix:
        return np.sum(y_tilde.round() == y_data.round()) /  y_tilde.size
    
    def error_name(self) -> str:
        """
            Returns the string that should be associated with the error_nn values
        """
        return "Accuracy"

    def perm_data(self, rng: np.random.Generator):
        """
            Permutes data for SDG
        """
        perm = rng.permuted(np.arange(0, self.n))
        self.X = self.X[perm, :]
        self.y = self.y[perm]  

