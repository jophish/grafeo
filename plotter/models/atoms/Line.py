from ...pens.Pen import Pen
from .Point import Point
from .Atom import Atom
from ..BoundingBox import BoundingBox

class Line(Atom):
    """
    The Line class is used to represent a line in a scene.

    Lines consist of any number of points, as well as a pen identifier.

    :ivar points: The points comprising the line
    :vartype points: list[class:`plotter.model.atoms.Point`]
    """

    points: list[Point]

    def __init__(self, points: list[Point], pen: Pen):
        """
        Initialize a line.

        :param points: A list of points
        :type points: list[class:`plotter.model.atoms.Point`]
        :param pen: A pen identifier
        :type pen: class:`plotter.pens.Pen`
        """
        super().__init__(pen=pen)
        self.points = points
        self.pen = pen

    def get_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the line.

        :return: Bounding box of the line
        :rtype: class:`plotter.models.BoundingBox`
        """
        bounding_box = BoundingBox()
        for point in self.points:
            bounding_box.update(point.get_bounding_box())
        return bounding_box
