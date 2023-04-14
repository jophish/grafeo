from scipy.interpolate import interp1d

from ...pens.Pen import Pen
from ..BoundingBox import BoundingBox
from .Atom import Atom


class Point(Atom):
    """
    The Point class represents an individual point in a scene.

    Points can exist independently in a scene, or be used to comprise other scene elements.
    When used to define other scene elements, the semantics of the pen associated with the
    point may be undefined.

    :ivar x: x coordinate of point
    :vartype x: float
    :ivar y: y coordinate of point
    :vartype y: float
    """

    def __init__(self, x: float, y: float, pen: Pen):
        """
        Initialize the point.

        :param x: x coordinate of point
        :param y: y coordinate of point
        :param pen: Pen to associate with the point
        """
        super().__init__(pen=pen)
        self.x = x
        self.y = y
        self._bounding_box = BoundingBox(
            min_x=self.x, max_x=self.x, min_y=self.y, max_y=self.y
        )

    def lerp(self, other: "Point", ratio: float) -> "Point":
        """
        Perform linear interpolation between this point and another.

        Treats points as two-dimensional vectors. A ratio of 0 returns a new
        point whose coordinates are identical to the original's; a ratio of 1
        will return a new point with coordinates identical to those of `other`.

        The pen type of the interpolated point will be the same as the originating point.

        :param other: Other point to lerp between
        :param ratio: Interpolation ratio
        :return: A new interpolated point
        """
        lerp_x = interp1d([0, 1], [self.x, other.x], fill_value="extrapolate")(ratio)
        lerp_y = interp1d([0, 1], [self.y, other.y], fill_value="extrapolate")(ratio)
        return Point(lerp_x, lerp_y, self.pen)

    def get_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the line.

        :return: Bounding box of the line
        """
        return self._bounding_box

    def translate(self, x: float, y: float):
        """
        Translate the point by x, y.

        :param x: Magnitude in x direction of translation
        :param y: Magnitude in y direction of translation
        """
        self.x += x
        self.y += y
        self._bounding_box.min_x += x
        self._bounding_box.max_x += x
        self._bounding_box.min_y += y
        self._bounding_box.max_y += y

    def make_bounding_box(self) -> BoundingBox:
        """
        Construct a bounding box on the fly.

        :return: The point's bounding box
        """
        return BoundingBox(min_x=self.x, max_x=self.x, min_y=self.y, max_y=self.y)
