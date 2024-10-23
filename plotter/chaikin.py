import math
from random import randint
from test import generate_line, sample_spline

from LineGenerator import NoiseLineGenerator
from main import run_prog
from py5 import Py5Vector, Sketch

WIDTH = 16640
HEIGHT = 10720

SCALE = 0.1


class TestSketch(Sketch):
    gpgl = []
    lines = []
    shapes = []

    def __init__(self):
        super().__init__()
        nlg = NoiseLineGenerator()
        self.lines = nlg.generate_lines()
        self.gpgl = nlg.generate_gpgl()

    def settings(self):
        self.size(round(WIDTH * SCALE), round(HEIGHT * SCALE))

    def setup(self):
        for line in self.lines:
            shape = self.make_shape_from_line(line)
            self.style_shape(shape)
            self.shapes.append(shape)
        for shape in self.shapes:
            self.shape(shape)

    def draw(self):
        return

    def style_shape(self, shape):
        shape.set_fill(False)
        shape.set_stroke_weight(20)
        shape.scale(SCALE)

    def make_shape_from_line(self, vectors: list[Py5Vector]):
        s = self.create_shape()
        s.begin_shape()
        for vector in vectors:
            s.vertex(vector.x, vector.y)
        s.end_shape()
        return s

    def make_incremental_gpgl(self, curve, translation_x, translation_y):
        for i in range(curve.get_vertex_count()):
            if i == 0:
                self.gpgl.append(
                    f"M{round(curve.get_vertex(i).x + translation_x)},{round(curve.get_vertex(i).y + translation_y)}"
                )
            self.gpgl.append(
                f"D{round(curve.get_vertex(i).x + translation_x)},{round(curve.get_vertex(i).y + translation_y)}"
            )

    def make_gpgl(self, curve, translation_x, translation_y):
        command = "D"

        for i in range(curve.get_vertex_count()):
            if i == 0:
                self.gpgl.append(
                    f"M{round(curve.get_vertex(i).x + translation_x)},{round(curve.get_vertex(i).y + translation_y)}"
                )

            command += f"{round(curve.get_vertex(i).x + translation_x)},{round(curve.get_vertex(i).y + translation_y)}"
            if i != (curve.get_vertex_count() - 1):
                command += ","

        self.gpgl.append(command)

    def make_curve(self, height, n_points, tightness):
        s = self.create_shape()
        s.begin_shape()
        s.curve_tightness(tightness)
        max_rand_mag = 2 * (WIDTH / n_points)
        for i in range(n_points):
            rand_mag = round((i / n_points) * max_rand_mag)
            x = (i * (WIDTH / n_points)) + randint(-rand_mag, rand_mag)
            y = height + randint(-rand_mag, rand_mag)
            s.curve_vertex(x, y)

        s.end_shape()
        return s

    def make_line(self, height, n_points):
        s = self.create_shape()
        s.begin_shape()
        max_rand_mag = 2 * (WIDTH / n_points)
        for i in range(n_points):
            rand_mag = round((i / n_points) * max_rand_mag)
            x = (i * (WIDTH / n_points)) + randint(-rand_mag, rand_mag)
            y = height + randint(-rand_mag, rand_mag)
            s.vertex(x, y)
        s.end_shape()
        return s

    def chaikin(self, shape, ratio, iterations, close):
        print(iterations)
        if iterations == 0:
            return shape

        next_shape = self.create_shape()
        next_shape.begin_shape()

        # Draw next iteration here
        num_corners = shape.get_vertex_count()
        if not close:
            num_corners -= 1

        for i in range(num_corners):
            v1 = shape.get_vertex(i)
            v2 = shape.get_vertex((i + 1) % shape.get_vertex_count())
            new_points = self.chaikin_cut(v1, v2, ratio)

            if (not close) and (i == 0):
                next_shape.vertex(v1.x, v1.y)
                next_shape.vertex(new_points[1].x, new_points[1].y)
            elif (not close) and (i == num_corners - 1):
                next_shape.vertex(new_points[0].x, new_points[0].y)
                next_shape.vertex(v2.x, v2.y)
            else:
                next_shape.vertex(new_points[0].x, new_points[0].y)
                next_shape.vertex(new_points[1].x, new_points[1].y)

        if close:
            next_shape.end_shape(self.CLOSE)
        else:
            next_shape.end_shape()

        return self.chaikin(next_shape, ratio, iterations - 1, close)

    def chaikin_cut(self, v1, v2, ratio):
        new_points = []

        if ratio > 0.5:
            ratio = 1 - ratio

        x = self.lerp(v1.x, v2.x, ratio)
        y = self.lerp(v1.y, v2.y, ratio)
        new_points.append(Py5Vector(x, y))

        x = self.lerp(v2.x, v1.x, ratio)
        y = self.lerp(v2.y, v1.y, ratio)
        new_points.append(Py5Vector(x, y))

        return new_points

    def chaikin_closed(self, shape, ratio, iterations):
        return self.chaikin(shape, ratio, iterations, True)

    def chaikin_open(self, shape, ratio, iterations):
        return self.chaikin(shape, ratio, iterations, False)


def main():
    sketch = TestSketch()
    sketch.run_sketch(block=False)
    input()
    print(sketch.gpgl[:6])
    input()
    run_prog(sketch.gpgl)


main()
