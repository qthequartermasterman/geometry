USE_EXACT = False
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
    from geometry.core.Circle import Circle
    from geometry.core.Construction import Construction

from geometry.core import EuclidConstructions

__all__ = [
    # core
    'Point', 'Line', 'Circle', 'Construction', 'EuclidConstructions'
]
