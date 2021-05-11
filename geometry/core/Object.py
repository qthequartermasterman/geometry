class Object:
    """
    Objects have dependencies and immediate dependents. These help us find topological orderings for constructions and
    quickly determine new points.
    """
    def __init__(self):
        self.dependencies: {Object} = set()  # All of the objects constructed prior to this one.
        self.dependents: {Object} = set()  # All of the objects that are constructed immediately using this one

    def set_dependencies(self, dependencies: set):
        self.dependencies = dependencies

    def __lt__(self, other):
        return hash(self) < hash(other)

