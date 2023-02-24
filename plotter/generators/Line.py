from py5 import Py5Vector
from enum import Enum

class Pen(Enum):
    ONE = 'ONE'
    TWO = 'TWO'
    THREE = 'THREE'
    FOUR = 'FOUR'
    FIVE = 'FIVE'
    SIX = 'SIX'
    SEVEN = 'SEVEN'
    EIGHT = 'EIGHT'

# The Line class represents a single, contiguous line consisting of 1 or more points.
# Points are represented as Py5Vectors
# Lines can have properties associated with them, including the pen to use.
class Line():

    pen: Pen
    points: list[Py5Vector]

    def __init__(self, points: list[Py5Vector], pen: Pen):
        self.points = points
        self.pen = pen

    def get_points(self):
        return self.points

    def set_points(self, points: list[Py5Vector]):
        self.points = points

    def get_pen(self):
        return self.pen

    def set_pen(self, pen: Pen):
        self.pen = pen
