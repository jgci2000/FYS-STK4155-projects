
import numpy as np
from .ActivationFunction import ActivationFunction

class ELU(ActivationFunction):
    """
        eLU activation function
    """

    def __init__(self, alpha: float = 5e-3):
        """
            Initialises eLU with small alpha
            Parameters:
                alpha (float): Should be fairly small
        """
        self._alpha = alpha
    
    def name(self) -> str:
        return 'ELU'

    def __call__(self, x: float) -> float:
        """
            Returns f(x)
        """
        return np.multiply((x >= 0), x) + np.multiply((x < 0), (np.exp(x) - 1.0) * self._alpha)

    def d(self, x: float) -> float:
        """
            Returns f'(x)
        """
        return (x >= 0) * 1 + np.multiply((x < 0), self._alpha * np.exp(x))
