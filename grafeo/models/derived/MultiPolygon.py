from ...pens.Pen import Pen
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
        # Get all models that are not the polygons defining the collection
        unique_models = list(filter(lambda x: x not in self._polygons, self.models))
        new_model = MultiPolygon([poly.copy() for poly in self._polygons], self.pen)
        for model in unique_models:
            new_model.add_model(model.copy())
        for line in self.lines:
            new_model.add_line(line.copy())
        for point in self.points:
            new_model.add_point(point.copy())
        return new_model

    def _make_shapely_geometry(self):
        self._shapely_geometry = shapely.MultiPolygon([polygon.shapely_geometry for polygon in self._polygons])
