import math

from py5 import Py5Vector, Sketch

from plotter.generators.Generator import Generator, GeneratorConfig
from plotter.generators.Line import Line


class GenSketch(Sketch):
    config: GeneratorConfig
    pens = {}
    generator: Generator

    def __init__(self, config: GeneratorConfig, pen_config):
        super().__init__()
        self.config = config
        self.pens = pen_config

    def set_generator(self, generator: Generator):
        self.generator = generator

    def set_pen_config(self, pen_config):
        self.pens = pen_config

    def settings(self):
        self.size(
            round(self.config["width"] * self.config["scale"]),
            round(self.config["height"] * self.config["scale"]),
        )

    def setup(self):
        self.no_loop()

    def draw(self):
        self.background(255, 255, 255)
        lines = self.generator.get_lines()
        for line in lines:
            shape = self.make_shape_from_line(line)
            self.shape(shape)

    def make_shape_from_line(self, line: Line):
        s = self.create_shape()
        s.begin_shape()
        for vector in line.get_points():
            s.vertex(vector.x, vector.y)
        s.end_shape()
        s.set_fill(False)

        pen = self.pens[str(line.get_pen_num())]
        s.set_stroke_weight(pen["weight"])
        s.set_stroke(pen["color"])
        s.scale(self.config["scale"])
        return s
