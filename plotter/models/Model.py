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

    def __init__(self):
        """Initialize a model."""
        self._lines: list[Line] = []
        self._points: list[Point] = []
        self._models: list["Model"] = []
        self._used_pens: set[Pen] = set()
        self._bounding_box = BoundingBox()
        pass

    def add_line(self, line: Line):
        """
        Add a line to this model.

        :param line: Line to add
        """
        self._lines.append(line)
        self._used_pens.add(line.pen)
        self._update_bounding_box(line)

    @property
    def lines(self):
        """Get the lines in this model."""
        return self._lines

    @property
    def models(self):
        """Get the models in this model."""
        return self._models

    @property
    def points(self):
        """Get the points in this model."""
        return self._models

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
        self._bounding_box.update(atom.get_bounding_box())

    def get_used_pens(self) -> set[Pen]:
        """
        Get a set of pens used in this model.

        :return: Set containing pens used.
        """
        return self._used_pens

    def get_dims(self) -> tuple[int, int]:
        """
        Get the dimensions of the model.

        :return: A tuple representing the width, height of the model.
        """
        pass

    def get_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the model.

        :return: The bounding box of the model
        """
        return self._bounding_box

    def normalize(self):
        """
        Normalize the model by translating it.

        Translates the model such that it is bound within the +x/+y quadrant.
        """
        translate_x = abs(min(0, self._bounding_box.min_x))
        translate_y = abs(min(0, self._bounding_box.min_y))

        for line in self._lines:
            line.translate(translate_x, translate_y)
        for point in self._points:
            point.translate(translate_x, translate_y)
        for model in self._models:
            model.normalize()
        self._bounding_box.min_x += translate_x
        self._bounding_box.max_x += translate_x
        self._bounding_box.min_y += translate_y
        self._bounding_box.max_y += translate_y

    def make_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the model.

        :return: The bounding box of the model
        """
        bounding_box = BoundingBox()
        for line in self._lines:
            bounding_box.update(line.make_bounding_box())
        for model in self._models:
            bounding_box.update(model.make_bounding_box())
        for point in self._points:
            bounding_box.update(point.make_bounding_box())
        return bounding_box
