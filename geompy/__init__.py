USE_EXACT = True  # Should we use the Exact algebra system (symengine/sympy) or inexact algebra system (numpy)?
USE_PURE_SYMPY = False

if USE_EXACT:
    from geompy.core.Object import Object
    from geompy.core.Point import Point
    from geompy.core.Line import Line
    from geompy.core.Circle import Circle
    from geompy.core.Construction import Construction
    from geompy.core.Angle import Angle
else:
    from geompy.core.Object import Object
    from geompy.core.Point import FastPoint as Point
    from geompy.core.Line import FastLine as Line
    from geompy.core.Circle import FastCircle as Circle
    from geompy.core.Construction import Construction
    from geompy.core.Angle import Angle

from geompy.core import *

__all__ = [
    # core
    'Object', 'Point', 'Line', 'Circle', 'Construction', 'EuclidConstructions'
]
