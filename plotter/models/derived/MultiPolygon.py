from plotter.pens.Pen import Pen
import shapely
from .Polygon import Polygon
from .mixins.Hatchable import Hatchable

class MultiPolygon(Hatchable):
    """
    The mulipolygon class is used to model a collection of polygons.
    """

    def __init__(self, polygons: list[Polygon], pen: Pen):
        """
        Initialize a polygon

        """
        super().__init__(models=polygons)
        self.pen = pen
        self._polygons = polygons

    def copy(self):
        return MultiPolygon([poly.copy() for poly in self._polygons], self.pen)

    def _make_shapely_geometry(self):
        self._shapely_geometry = shapely.MultiPolygon([polygon.shapely_geometry for polygon in self._polygons])
