from plotter.model.atoms.Line import Line
from plotter.model.atoms.Point import Point

class Model():
    """
    The Model class is used to model a generated scene. It consists of any number of atomic
    units (Atoms) or Models, which together comprise the scene.

    ...
    Attributes
    ----------
    used_pens : list[int]
    """

    def __init__(self):
        self.used_pens = []

        self.lines = []
        self.points = []
        self.models = []

        self.max_x = None
        self.max_y = None

        self.min_x = None
        self.min_y = None

    def add_line(line: Line):
        pass

    def add_point(point: Point):
        pass

    def add_model(self, model: Model):
        pass

    def get_bounding_box(self):
        pass
