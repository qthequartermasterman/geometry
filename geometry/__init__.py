USE_EXACT = True  # Should we use the Exact algebra system (symengine) or inexact algebra system (numpy)?

if USE_EXACT:
    from geometry.core.Object import Object
    from geometry.core.Point import Point
    from geometry.core.Line import Line
    from geometry.core.Circle import Circle
    from geometry.core.Construction import Construction
else:
    from geometry.core.Object import Object
    from geometry.core.Point import FastPoint as Point
    from geometry.core.Line import FastLine as Line
    from geometry.core.Circle import FastCircle as Circle
    from geometry.core.Construction import Construction

from geometry.core import *

__all__ = [
    # core
    'Object', 'Point', 'Line', 'Circle', 'Construction', 'EuclidConstructions'
]
