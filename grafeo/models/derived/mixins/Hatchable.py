from ...Model import Model, BaseModel
from ...atoms.Point import Point
from ...atoms.Line import Line
from ....pens.Pen import Pen
import math
import shapely


class Hatchable(BaseModel):
    """
    Hatchable encpasulates the notion of a model that is able to be sensibly hatched.

    This requires the model to consist of some number of closed regions.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super().__init__(*args, **kwargs)
        pass

    def hatch(self, pen: Pen, angle: float, spacing: float):
        """
        Return a model representing the hatched area of the model.

        :param pen: Pen to hatch with
        :angle float: Angle to draw hatched lines. Between -90 and 90.
        :spacing float: Distance between hatched lines
        """

        # Strategy:
        # - Find minimum hatch line distance s.t. it will always cover the bounding box
        # - Draw lines spacing apart s.t box is definitely covered
        # - Get intersection of these lines and the bounding box of this shape

        height = self._bounding_box.max_y - self._bounding_box.min_y
        width = self._bounding_box.max_x - self._bounding_box.min_x

        origin_x = self._bounding_box.min_x
        origin_y = self._bounding_box.max_y

        hatch_x_offset = abs(math.tan(math.pi * angle / 180.0) * height)
        hatch_model = Model()
        num_lines = round((width + 2 * hatch_x_offset) / spacing)

        # Make sure to alternate the direction we approach from to make the
        # plotter's life easier. "Boustrophedonically", colloquially.
        line_strings = []
        for i in range(num_lines):
            start_x = origin_x - hatch_x_offset
            top_point = Point(start_x + i * spacing, origin_y, pen)
            bottom_point = Point(start_x + (i * spacing) - (math.copysign(1, angle) * hatch_x_offset), origin_y - height, pen)
            line = None
            if i % 2:
                line = [top_point, bottom_point]
            else:
                line = [bottom_point, top_point]
            hatch_model.add_line(Line(
                line,
                pen
            ))
            line_strings.append(shapely.LineString([[line[0].x, line[0].y], [line[1].x, line[1].y]]))

        hatch_intersection = hatch_model.intersection(self)
        self.add_model(hatch_intersection)
        return hatch_intersection
