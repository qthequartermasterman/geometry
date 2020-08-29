class Object:
    def __init__(self):
        self.dependencies = set()

    def set_dependencies(self, dependencies: set):
        self.dependencies = dependencies