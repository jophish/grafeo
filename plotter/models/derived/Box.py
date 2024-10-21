from ..Model import Model
from ..atoms.Point import Point
from ..atoms.Line import Line
from plotter.pens.Pen import Pen
import math

class Box(Model):
    """
    The Box class is used to model a... box.
    """

    def __init__(self, width: float, height: float, origin_x: float, origin_y: float):
        """
        Initialize a box.

        :param width: width of box
        :param height: height of box
        :param origin_x: x coordinate of top-left corner of box
        :param origin_y: y coordinate of top-left corner of box
        """
        super().__init__()
        self.width = width
        self.height = height
        self.origin_x = origin_x
        self.origin_y = origin_y

    def hatch(self, pen: Pen, angle: float, spacing: float):
        """
        Hatches the box.

        :param pen: Pen to hatch with
        :angle float: Angle to draw hatched lines. Between -90 and 90.
        :spacing float: Distance between hatched lines
        """

        # Strategy:
        # - Find minimum hatch line distance s.t. it will always cover the box
        # - Draw lines spacing apart s.t box is definitely covered
        # - Get intersection of these lines and the bounding box of this box
        hatch_x_offset = abs(math.tan(math.pi * angle / 180.0) * self.height)
        hatch_model = Model()
        num_lines = round((self.width + 2 * hatch_x_offset) / spacing)

        # Make sure to alternate the direction we approach from to make the
        # plotter's life easier.
        for i in range(num_lines):
            start_x = self.origin_x - hatch_x_offset
            top_point = Point(start_x + i * spacing, self.origin_y, pen)
            bottom_point = Point(start_x + (i * spacing) - (math.copysign(1, angle) * hatch_x_offset), self.origin_y - self.height, pen)
            if i % 2:
                hatch_model.add_line(Line(
                    [
                        top_point,
                        bottom_point
                    ],
                    pen
                ))
            else:
                hatch_model.add_line(Line(
                    [
                        bottom_point,
                        top_point
                    ],
                    pen
                ))
        hatch_intersection = hatch_model.intersection(self._bounding_box)
        self.add_model(hatch_intersection)

    def draw_outline(self, pen: Pen):
        """
        Draws the outline of the box.
        """
        top_left_corner = Point(self.origin_x, self.origin_y, pen)
        top_right_corner = Point(self.origin_x + self.width, self.origin_y, pen)
        bottom_right_corner = Point(self.origin_x + self.width, self.origin_y - self.height, pen)
        bottom_left_corner = Point(self.origin_x, self.origin_y - self.height, pen)

        self.add_line(
            Line(
                [
                    top_left_corner,
                    top_right_corner
                ],
                pen
            )
        )
        self.add_line(
            Line(
                [
                    top_right_corner,
                    bottom_right_corner
                ],
                pen
            )
        )
        self.add_line(
            Line(
                [
                    bottom_right_corner,
                    bottom_left_corner
                ],
                pen
            )
        )
        self.add_line(
            Line(
                [
                    bottom_left_corner,
                    top_left_corner
                ],
                pen
            )
        )
