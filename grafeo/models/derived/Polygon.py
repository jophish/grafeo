from ..atoms.Line import Line
from ...pens.Pen import Pen
from .mixins.Hatchable import Hatchable
import shapely

class Polygon(Hatchable):
    """
    The polygon class is used to model a closed polygon.

    The polygon must have identical start and end points, and
    is assumed to not self-intersect.
    """

    def __init__(self, line: Line, pen: Pen, holes = None):
        """
        Initialize a polygon

        """
        self._holes = holes if holes else []
        self._poly_line = line
        self.pen = pen
        super().__init__(lines=[line] + self._holes)

    def copy(self):
        # Get all lines that are not the lines/holes defining the polygon
        unique_lines = list(filter(lambda x: x != self._poly_line and x not in self._holes, self.lines))
        new_model = Polygon(self._poly_line.copy(), self.pen, [hole.copy() for hole in self._holes])

        for model in self.models:
            new_model.add_model(model.copy())
        for line in unique_lines:
            new_model.add_line(line.copy())
        for point in self.points:
            new_model.add_point(point.copy())
        return new_model

    def _make_shapely_geometry(self):
        line = self._lines[0]
        holes = [[[point.x, point.y] for point in hole_line.points] for hole_line in self._holes]
        self._shapely_geometry = shapely.Polygon([[point.x, point.y] for point in line.points], holes)
