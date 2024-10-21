from dataclasses import dataclass
from plotter.utils.intersection import intersects, points_are_epsilon_close

@dataclass
class BoundingBox:
    """Class for representing the bounding box of some two-dimensional area."""

    min_x: float = float("inf")
    max_x: float = float("-inf")
    min_y: float = float("inf")
    max_y: float = float("-inf")

    def update(self, other: "BoundingBox"):
        """
        Update the current bounds given another bounding box.

        :param other: Another bounding box
        """
        self.min_x = min(self.min_x, other.min_x)
        self.max_x = max(self.max_x, other.max_x)
        self.min_y = min(self.min_y, other.min_y)
        self.max_y = max(self.max_y, other.max_y)

    def find_intersections(self, x1: float, y1: float, x2: float, y2: float):
        """
        Find the intersections between bounding box and line defined by two points.
        """
        box_top_left = (self.min_x, self.max_y)
        box_top_right = (self.max_x, self.max_y)
        box_bottom_right = (self.max_x, self.min_y)
        box_bottom_left = (self.min_x, self.min_y)
        # Remove duplicates, in case we intersect a corner (since it will hit for 2 lines)
        intersections = list(set(list(filter(lambda x: x != None, [
            intersects(box_top_left, box_top_right, (x1, y1), (x2, y2)),
            intersects(box_top_right, box_bottom_right, (x1, y1), (x2, y2)),
            intersects(box_bottom_right, box_bottom_left, (x1, y1), (x2, y2)),
            intersects(box_bottom_left, box_top_left, (x1, y1), (x2, y2))
        ]))))

        return intersections

    def point_is_on_corner(self, x: float, y: float) -> bool:
        """
        Determine if a given point is essentially on a corner
        """
        point = (x, y)
        box_top_left = (self.min_x, self.max_y)
        box_top_right = (self.max_x, self.max_y)
        box_bottom_right = (self.max_x, self.min_y)
        box_bottom_left = (self.min_x, self.min_y)
        return any([
            points_are_epsilon_close(point, box_top_left),
            points_are_epsilon_close(point, box_top_right),
            points_are_epsilon_close(point, box_bottom_right),
            points_are_epsilon_close(point, box_bottom_left),
        ])
