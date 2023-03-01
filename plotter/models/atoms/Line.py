from enum import Enum

# The Line class represents a single, contiguous line consisting of 1 or more points.
# Points are represented as Py5Vectors
# Lines can have properties associated with them, including the pen to use.
class Line():

    pen_num: int
    points: list[Py5Vector]

    def __init__(self, points: list[Py5Vector], pen_num: int):
        self.points = points
        self.pen_num = pen_num

    def get_points(self):
        return self.points

    def set_points(self, points: list[Py5Vector]):
        self.points = points

    def get_pen_num(self):
        return self.pen_num

    def set_pen_num(self, pen_num: int):
        self.pen_num = pen_num
