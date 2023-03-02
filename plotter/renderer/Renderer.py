import array
import io
import math

import cairo
import numpy

from plotter.generators.Line import Line

MAX_RENDER_WIDTH = 3000
MAX_RENDER_HEIGHT = 3000


class Renderer:
    def __init__(self, pen_config, pen_mapping):
        super().__init__()
        self.pen_config = pen_config
        self.pen_mapping = pen_mapping

    def set_lines(self, lines: list[Line]):
        self.lines = lines

    def set_scale_factor(self, width, height):
        self.scale = min(1, MAX_RENDER_WIDTH / width, MAX_RENDER_HEIGHT / height)

    def render(self, lines: list[Line], width, height):
        self.set_scale_factor(width, height)
        h = round(height * self.scale)
        w = round(width * self.scale)
        data = numpy.zeros(shape=(h * w * 4), dtype=numpy.uint8)
        data = data.view(numpy.uint32).reshape((h, w))
        surface = cairo.ImageSurface.create_for_data(data, cairo.Format.ARGB32, w, h)
        self.ctx = cairo.Context(surface)
        self.ctx.save()
        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.paint()
        self.ctx.restore()
        for line in lines:
            self.draw_line(line)

        data_view = data.view(numpy.uint8).reshape((h * w * 4)).astype(numpy.float32)
        data_view /= 255
        return {"data": data_view, "height": h, "width": w}

    def draw_line(self, line):
        points = line.get_points()
        if not len(points):
            return
        self.ctx.set_line_width(1)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.move_to(points[0].x * self.scale, points[0].y * self.scale)
        for point in points:
            self.ctx.line_to(point.x * self.scale, point.y * self.scale)
        self.ctx.stroke()
