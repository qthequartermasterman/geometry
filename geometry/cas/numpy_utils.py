from symengine import sympify as symengine_sympify
import numpy as np


def sympify(x):
    return np.array(float(symengine_sympify(x).evalf()))


def identity(x):
    return x


Expression = np.ndarray