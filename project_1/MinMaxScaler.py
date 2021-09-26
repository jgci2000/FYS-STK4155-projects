
import numpy as np
from Scaler import Scaler

class MinMaxScaler(Scaler):
    """
        Applies min-max scaling to the design matrix by remapping from min..max to 0..1
    """
    
    def prepare(self, X: np.matrix):
        """
            Samples the basis design matrix to obtain the min and max
            Parameters:
                X (np.matrix): Principal design matrix
        """
        
        if X.shape[1] == 1:
            self._min = np.min(X[:, 0])
            self._max = np.max(X[:, 0])
        else:
            self._min = np.zeros(X.shape[1] - 1)
            self._max = np.zeros(X.shape[1] - 1)
            
            for i in range(1, X.shape[1]):
                self._min[i - 1] = np.min(X[:, i])
                self._max[i - 1] = np.max(X[:, i])

    def scale(self, X: np.matrix) -> np.matrix:
        """
            Scales the design matrix by remapping from min..max to 0..1
            Parameters:
                X (np.matrix): Design matrix to scale
        """
        
        X_scaled = np.ones(X.shape)
        
        if X.shape[1] == 1:
            X_scaled[:, 0] = (X[:, 0] - self._min) / (self._max - self._min)
        else:
            for i in range(1, X.shape[1]):
                X_scaled[:, i] = (X[:, i] - self._min[i - 1]) / (self._max[i - 1] - self._min[i - 1])
        
        return X_scaled