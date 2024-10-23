from ..atoms.Line import Line
from plotter.pens.Pen import Pen
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
        self.pen = pen
        super().__init__(lines=[line] + self._holes)

    def copy(self):
        return Polygon(self.lines[0].copy(), self.pen, [hole.copy() for hole in self._holes])

    def _make_shapely_geometry(self):
        line = self._lines[0]
        holes = [[[point.x, point.y] for point in hole_line.points] for hole_line in self._holes]
        self._shapely_geometry = shapely.Polygon([[point.x, point.y] for point in line.points], holes)
