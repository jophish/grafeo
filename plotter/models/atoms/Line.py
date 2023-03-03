from ...pens import Pen
from ..BoundingBox import BoundingBox
from .Atom import Atom
from .Point import Point


class Line(Atom):
    """
    The Line class is used to represent a line in a scene.

    Lines consist of any number of points, as well as a pen identifier.

    :ivar points: The points comprising the line
    :vartype points: list[:class:`Point`]
    """

    def __init__(self, points: list[Point], pen: Pen):
        """
        Initialize a line.

        :param points: A list of points
        :param pen: A pen identifier
        """
        super().__init__(pen=pen)
        self.points = points
        self.pen = pen

    def get_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the line.

        :return: Bounding box of the line
        """
        bounding_box = BoundingBox()
        for point in self.points:
            bounding_box.update(point.get_bounding_box())
        return bounding_box

    def translate(self, x: float, y: float):
        """
        Translate the line by x, y.

        :param x: Magnitude in x direction of translation
        :param y: Magnitude in y direction of translation
        """
        (point.translate(x, y) for point in self.points)

    def lerp(self, other: "Line", ratio: float):
        """
        Perform linear interpolation between this line and another.

        Interpolates
        """
        # Each line is comprised of segments; each segment has a length. Each line has a total length.
        pass

    def lerp_points(self, other: "Line", ratio: float) -> "Line":
        """
        Perform linear interpolation between individual points of two lines.

        Each line must have the same number of points, else interpolation will fail.
        The pen type of the interpolated line will be the same as the originating line.

        :param other: Other line to interpolate towards
        :param ratio: Interpolation ratio
        :return: New line, with inteprolated points
        """
        if len(self.points) != len(other.points):
            raise Exception("Lines have non-equal number of points")

        return Line(
            [p1.lerp(p2, ratio) for (p1, p2) in zip(self.points, other.points)],
            self.pen,
        )
