from dataclasses import dataclass


@dataclass
class BoundingBox:
    """Class for representing the bounding box of some two-dimensional area."""

    min_x: float = float('inf')
    max_x: float = float('-inf')
    min_y: float = float('inf')
    max_y: float = float('-inf')

    def update(self, other: 'BoundingBox'):
        """
        Update the current bounds given another bounding box.

        :param other: Another bounding box
        """
        self.min_x = min(self.min_x, other.min_x)
        self.max_x = max(self.max_x, other.max_x)
        self.min_y = min(self.min_y, other.min_y)
        self.max_y = max(self.max_y, other.max_y)
