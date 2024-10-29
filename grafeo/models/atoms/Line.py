from ...pens import Pen
from ..BoundingBox import BoundingBox
from .Atom import Atom
from .Point import Point
import shapely

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
        self.points = [point.copy() for point in points]
        self.pen = pen
        self._bounding_box = self._make_bounding_box()

    @property
    def shapely_geometry(self):
        self._make_shapely_geometry()
        return self._shapely_geometry

    def _make_shapely_geometry(self):
        points = [[point.x, point.y] for point in self.points]
        self._shapely_geometry = shapely.LineString(points)

    def copy(self) -> "Line":
        """Create a deep-copy of the current Line."""
        return Line([point.copy() for point in self.points], self.pen)

    def intersection(self, bounding_box: BoundingBox) -> list["Line"]:
        """
        Create new line(s) from existing which intersects a given bounding box.

        This may result in several new, noncontiguous lines being created.
        """
        new_lines = []
        current_line_points = []
        for i in range(len(self.points) - 1):
            start_point = self.points[i]
            end_point = self.points[i+1]
            start_point_inside = self.points[i].is_within_bounds(bounding_box)
            end_point_inside = self.points[i+1].is_within_bounds(bounding_box)
            if (start_point_inside and end_point_inside):
                if len(current_line_points) == 0:
                    current_line_points.append(start_point.copy())
                current_line_points.append(end_point.copy())

            elif (not start_point_inside and not end_point_inside):
                # Two cases:
                #  - Passes through no edges
                #  - Passes through two edges
                intersections = bounding_box.find_intersections(
                    start_point.x,
                    start_point.y,
                    end_point.x,
                    end_point.y
                )
                if len(intersections) == 0:
                    continue
                elif len(intersections) == 2:
                    current_line_points.append(Point(intersections[0][0], intersections[0][1], self.pen))
                    current_line_points.append(Point(intersections[1][0], intersections[1][1], self.pen))
                    new_lines.append(Line(current_line_points, self.pen))
                    current_line_points = []
                else:
                    # 3 intersections could occur exactly when line begins or ends on a corner of
                    # the bounding box. Figure out which case we're in.
                    start_on_corner = bounding_box.point_is_on_corner(start_point.x, start_point.y)
                    if start_on_corner:
                        current_line_points.append(Point(start_point.x, start_point.y, self.pen))
                        current_line_points.append(Point(intersections[0][0], intersections[0][1], self.pen))
                        new_lines.append(Line(current_line_points, self.pen))
                        current_line_points = []
                    else:
                        current_line_points.append(Point(intersections[0][0], intersections[0][1], self.pen))
                        current_line_points.append(Point(end_point.x, end_point.y, self.pen))
                        new_lines.append(Line(current_line_points, self.pen))
                        current_line_points = []
            elif (start_point_inside and not end_point_inside):
                if len(current_line_points) == 0:
                    current_line_points.append(start_point.copy())
                current_line_points.append(end_point.copy())
                intersections = bounding_box.find_intersections(
                    start_point.x,
                    start_point.y,
                    end_point.x,
                    end_point.y
                )

                current_line_points.append(Point(intersections[0][0], intersections[0][1], self.pen))
                new_lines.append(Line(current_line_points, self.pen))
                current_line_points = []
            else:
                # End point inside and start point outside
                intersections = bounding_box.find_intersections(
                    start_point.x,
                    start_point.y,
                    end_point.x,
                    end_point.y
                )
                current_line_points.append(Point(intersections[0][0], intersections[0][1], self.pen))
                current_line_points.append(Point(end_point.x, end_point.y, self.pen))

        # If we've gotten though everything and still have points on the working line,
        # add it to the new_lines list
        if len(current_line_points) > 0:
            new_lines.append(Line(current_line_points, self.pen))
        return new_lines

    def _make_bounding_box(self) -> BoundingBox:
        """
        Construct a bounding box on the fly.

        :return: The line's bounding box
        """
        bounding_box = BoundingBox()
        for point in self.points:
            bounding_box.update(point.get_bounding_box())

        return bounding_box

    def make_bounding_box(self) -> BoundingBox:
        """
        Construct a bounding box on the fly.

        :return: The line's bounding box
        """
        bounding_box = BoundingBox()
        for point in self.points:
            bounding_box.update(point.make_bounding_box())
        return bounding_box

    def add_point(self, point: Point):
        """
        Add a point to the line.

        :param point: Point to add.
        """
        self.points.append(point)
        self._bounding_box.update(point.get_bounding_box())

    def get_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the line.

        :return: Bounding box of the line
        """
        return self._bounding_box

    def translate(self, x: float, y: float):
        """
        Translate the line by x, y.

        :param x: Magnitude in x direction of translation
        :param y: Magnitude in y direction of translation
        """
        for point in self.points:
            point.translate(x, y)
        self._bounding_box.min_x += x
        self._bounding_box.max_x += x
        self._bounding_box.min_y += y
        self._bounding_box.max_y += y

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

    def rotate(self, deg, x, y):
        """
        Rotates the line by deg about the point x, y.

        :param deg: Degrees to rotate by
        :param x: x coordinate of point to rotate about
        :param y: y coordinate of point to rotate about
        """
        for point in self.points:
            point.rotate(deg, x, y)
        self._bounding_box = self.make_bounding_box()

    def apply_matrix(self, matrix):
        for point in self.points:
            point.apply_matrix(matrix)
        self._bounding_box = self.make_bounding_box()
