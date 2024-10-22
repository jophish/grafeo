from ..pens.Pen import Pen
from .atoms.Atom import Atom
from .atoms.Line import Line
from .atoms.Point import Point
from .Bounded import Bounded
from .BoundingBox import BoundingBox
import shapely

class Model(Bounded):
    """
    The Model class is used to model a generated scene.

    A scene consists of any number of Atoms, or, recursively, Models.
    """

    def __init__(self, lines = None, points = None, models = None):
        """Initialize a model."""
        self._lines: list[Line] = lines if lines else []
        self._points: list[Point] = points if points else []
        self._models: list["Model"] = models if models else []
        self._used_pens: set[Pen] = set()
        self._bounding_box = BoundingBox()

        for atom in self._lines + self._points + self._models:
            self._update_bounding_box(atom)

    def _make_shapely_geometry(self):
        geometries = []
        if len(self._points) > 0:
            geometries.append(shapely.multipoints([point.shapely_geometry for point in self._points]))
        if len(self._lines) > 0:
            geometries.append(shapely.multilinestrings([line.shapely_geometry for line in self._lines]))
        if len(self._models) > 0:
            geometries.append(shapely.geometrycollections([model.shapely_geometry for model in self._models]))
        self._shapely_geometry = shapely.GeometryCollection(geometries)

    def is_empty(self):
        return len(self.models) == 0 and len(self.lines) == 0 and len(self.points) == 0

    def copy(self) -> "Model":
        new_model = Model()
        for model in self.models:
            new_model.add_model(model.copy())
        for line in self.lines:
            new_model.add_line(line.copy())
        for point in self.points:
            new_model.add_point(point.copy())
        return new_model

    def intersection(self, model: "Model") -> "Model":
        """
        Return a new model, which represents the interserction of this model and another

        Currently, this removes pen information. TODO: fix.
        """
        new_model = Model()
        shapely_intersection = self.shapely_geometry.intersection(model.shapely_geometry)
        print(shapely_intersection.geom_type)
        if shapely_intersection.geom_type == 'MultiLineString':
            for line_string in shapely_intersection.geoms:
                new_model.add_line(Line([Point(coord[0], coord[1], Pen.One) for coord in line_string.coords], Pen.One))
        return new_model

    def add_line(self, line: Line):
        """
        Add a line to this model.

        :param line: Line to add
        """
        self._lines.append(line)
        self._update_bounding_box(line)

    @property
    def shapely_geometry(self):
        self._make_shapely_geometry()
        return self._shapely_geometry

    @property
    def lines(self):
        """Get the lines in this model."""
        return self._lines

    @property
    def all_lines(self):
        """Gets all lines in this model, including those in submodels."""
        lines = [line for line in self._lines]
        for model in self._models:
            lines += model.all_lines
        return lines

    @property
    def models(self):
        """Get the models in this model."""
        return self._models

    @property
    def points(self):
        """Get the points in this model."""
        return self._points

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
        self._update_bounding_box(model)

    def _update_bounding_box(self, atom: Bounded):
        self._bounding_box.update(atom.get_bounding_box())

    def get_used_pens(self) -> set[Pen]:
        """
        Get a set of pens used in this model.

        :return: Set containing pens used.
        """
        used_pens: set[Pen] = set()
        for line in self._lines:
            used_pens = used_pens.union(set([line.pen]))
        for model in self._models:
            used_pens = used_pens.union(model.get_used_pens())
        return used_pens

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

    def translate(self, x, y):
        for line in self._lines:
            line.translate(x, y)
        for point in self._points:
            point.translate(x, y)
        for model in self._models:
            model.translate(x, y)
        self._bounding_box.min_x += x
        self._bounding_box.max_x += x
        self._bounding_box.min_y += y
        self._bounding_box.max_y += y

    def rotate(self, deg, x, y):
        """
        Rotates the model by deg about the point x, y.

        :param deg: Degrees to rotate by
        :param x: x coordinate of point to rotate about
        :param y: y coordinate of point to rotate about
        """
        for line in self._lines:
            line.rotate(deg, x, y)
        for point in self._points:
            point.rotate(deg, x, y)
        for model in self._models:
            model.rotate(deg, x, y)
        self._bounding_box = self.make_bounding_box()

    def apply_matrix(self, matrix):
        for line in self._lines:
            line.apply_matrix(matrix)
        for point in self._points:
            point.apply_matrix(matrix)
        for model in self._models:
            model.apply_matrix(matrix)
        self._bounding_box = self.make_bounding_box()
