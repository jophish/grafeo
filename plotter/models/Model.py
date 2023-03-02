from ..pens.Pen import Pen
from .atoms.Atom import Atom
from .atoms.Line import Line
from .atoms.Point import Point
from .Bounded import Bounded
from .BoundingBox import BoundingBox


class Model(Bounded):
    """
    The Model class is used to model a generated scene.

    A scene consists of any number of Atoms, or, recursively, Models.
    """

    _lines: list[Line] = []
    _points: list[Point] = []
    _models: list["Model"] = []

    _used_pens: list[Pen] = []

    _bounding_box: BoundingBox

    def __init__(self):
        """Initialize a model."""
        pass

    def add_line(self, line: Line):
        """
        Add a line to this model.

        :param line: Line to add
        """
        self._lines.append(line)
        self._update_bounding_box(line)

    def add_point(self, point: Point):
        """
        Add a point to this model.

        :param point: Point to add
        """
        self._points.append(point)

    def add_model(self, model: "Model"):
        """
        Add a sub-model to this model.

        :param model: Model to add
        """
        self._models.append(model)

    def _update_bounding_box(self, atom: Atom):
        pass

    def get_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the model.

        :return: The bounding box of the model
        """
        bounding_box = BoundingBox()
        for line in self._lines:
            bounding_box.update(line.get_bounding_box())
        for model in self._models:
            bounding_box.update(model.get_bounding_box())
        for point in self._points:
            bounding_box.update(point.get_bounding_box())
        return self._bounding_box
