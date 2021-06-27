from geompy import USE_EXACT, USE_PURE_SYMPY

use_numpy = not USE_EXACT

if use_numpy:
    from .numpy_utils import (sympify,
                              identity as simplify,
                              identity as fullsimplify,
                              Expression,
                              equals as equals)
    from numpy import (sqrt,
                       # allclose as equals,
                       inf as Infinity,
                       float32 as Expr,
                       isnan as is_nan)

else:
    if USE_PURE_SYMPY:
        from sympy import (sympify,
                           sqrt,
                           oo as Infinity,
                           Expr)
    else:
        from symengine import (sympify,
                               sqrt,
                               oo as Infinity,
                               Expr)
    from .symengine_utils import (symengine_equality as equals,
                                  optimized_simplify as simplify,
                                  Expression,
                                  is_nan,
                                  full_simplify)

alphabet = list(map(chr, range(97, 123)))
