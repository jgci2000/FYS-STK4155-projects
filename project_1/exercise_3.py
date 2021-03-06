import numpy as np
import matplotlib.pyplot as plt
from time import time

from functions import Regression


# parameters
max_degree = 15
n = 600
noise = 0.25
max_bootstrap = 100
n_folds_vals = [5, 7, 10]
degrees = np.arange(1, max_degree + 1)

# rng and seed
seed = 1963

# figure plot
plt.figure("MSE comparison", figsize=(9, 7))

# cross validation
for j, n_folds in enumerate(n_folds_vals):
    # regression object
    reg = Regression(max_degree, n, noise, seed)

    mse_cv = np.zeros(max_degree)
    for i, deg in enumerate(degrees):
        mse_cv[i] = reg.k_folds_cross_validation(degree=deg, n_folds=n_folds)
    
    plt.subplot(2, 2, j+1)
    
    plt.plot(degrees, mse_cv, '-k')
    plt.xlabel(r"complexity")
    plt.ylabel(r"MSE")
    plt.title(f"k-folds cross validation with k={n_folds}")

# bootstrap
# regression object
reg = Regression(max_degree, n, noise, seed)

mse = np.zeros(max_degree)
bias = np.zeros(max_degree)
var = np.zeros(max_degree)

for i, deg in enumerate(range(1, max_degree + 1)):
    mse[i], bias[i], var[i] = reg.bootstrap(degree=deg, max_bootstrap_cycle=max_bootstrap)

plt.subplot(2, 2, 4)
plt.plot(degrees, mse, '-r')
plt.xlabel(r"complexity")
plt.ylabel(r"MSE")
plt.title(f"bootstrap with n_cycles={max_bootstrap}")

plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.95, 
                    top=0.95, 
                    wspace=0.25, 
                    hspace=0.25)

plt.savefig(f"./images/ex3_cv_bs_n_{n}_noise_{noise}.pdf", dpi=400)

# plt.show()

