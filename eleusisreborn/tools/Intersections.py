import numpy as np
import matplotlib.pyplot as plt

def intersection(f_array,g_array):
    plt.plot(x, f, '-')
    plt.plot(x, g, '-')
    idx = np.argwhere(np.diff(np.sign(f - g)) != 0).reshape(-1) + 0
    plt.plot(x[idx], f[idx], 'ro')
    plt.show()
    return idx



