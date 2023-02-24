from py5 import Sketch, Py5Vector
import math
from plotter.generators.impl.NoiseLineGenerator import NoiseLineGenerator
from plotter.generators.Generator import Generator, GeneratorConfig
from plotter.generators.Line import Line

WIDTH = 16640
HEIGHT = 10720

SCALE = .1

class GenSketch(Sketch):

    config: GeneratorConfig
    generator: Generator

    def __init__(self, config: GeneratorConfig):
        super().__init__()
        self.config = config

    def set_generator(self, generator: Generator):
        self.generator = generator

    def settings(self):
        self.size(round(self.config['width']*SCALE), round(self.config['height']*SCALE))

    def setup(self):
        self.no_loop()

    def draw(self):
        self.background(255, 255, 255)
        lines = self.generator.get_lines()
        for line in lines:
            shape = self.make_shape_from_line(line)
            self.style_shape(shape)
            self.shape(shape)

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

