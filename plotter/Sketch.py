from py5 import Sketch, Py5Vector
import math
from plotter.generators.impl.NoiseLineGenerator import NoiseLineGenerator
from plotter.generators.Generator import Generator
from plotter.generators.Line import Line

WIDTH = 16640
HEIGHT = 10720

SCALE = .1

class TestSketch(Sketch):

    def __init__(self, generator: Generator):
        super().__init__()
        self.generator = generator({
            'width': WIDTH,
            'height': HEIGHT
        })

    def settings(self):
        self.size(round(WIDTH*SCALE), round(HEIGHT*SCALE))

    def setup(self):
        lines = self.generator.generate_lines()
        for line in lines:
            shape = self.make_shape_from_line(line)
            self.style_shape(shape)
            self.shape(shape)

    def draw(self):
        return

    def style_shape(self, shape):
        shape.set_fill(False)
        shape.set_stroke_weight(20)
        shape.scale(SCALE)

    def make_shape_from_line(self, line: Line):
        s = self.create_shape()
        s.begin_shape()
        for vector in line.get_points():
            s.vertex(vector.x, vector.y)
        s.end_shape()
        return s


def main():
    sketch = TestSketch(NoiseLineGenerator)
    sketch.run_sketch(block=False)

main()
