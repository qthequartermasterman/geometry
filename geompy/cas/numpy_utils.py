from symengine import sympify as symengine_sympify, Expr
import numpy as np


def sympify(x):
    if isinstance(x, Expr) or isinstance(x, str):
        print(x, type(x))

        sym = symengine_sympify(x)
        ev = sym.evalf()
        f = ev
        return np.array(f)
    else:
        return x


def identity(x):
    return x

def equals(x,y):
    x = np.array(x, dtype=np.float16)
    y = np.array(y, dtype=np.float16)
    np.array_equal(x,y)



Expression = np.ndarray