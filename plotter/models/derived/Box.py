from ..Model import Model
from ..atoms.Point import Point
from ..atoms.Line import Line
from plotter.pens.Pen import Pen
import math
from .Polygon import Polygon

class Box(Polygon):
    """
    The Box class is used to model a... box.
    """

    def __init__(self, width: float, height: float, origin_x: float, origin_y: float, pen: Pen):
        """
        Initialize a box.

        :param width: width of box
        :param height: height of box
        :param origin_x: x coordinate of top-left corner of box
        :param origin_y: y coordinate of top-left corner of box
        """

        self.width = width
        self.height = height
        self.origin_x = origin_x
        self.origin_y = origin_y
        line = self._make_lines(pen)
        super().__init__(line, pen)

    def _make_lines(self, pen: Pen):
        top_left_corner = Point(self.origin_x, self.origin_y, pen)
        top_right_corner = Point(self.origin_x + self.width, self.origin_y, pen)
        bottom_right_corner = Point(self.origin_x + self.width, self.origin_y - self.height, pen)
        bottom_left_corner = Point(self.origin_x, self.origin_y - self.height, pen)

        return Line(
                [
                    top_left_corner,
                    top_right_corner,
                    bottom_right_corner,
                    bottom_left_corner,
                    top_left_corner
                ],
                pen
            )
