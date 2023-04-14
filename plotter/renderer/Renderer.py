import math

import cairo
import numpy

from plotter.models import Model
from plotter.models.atoms import Line
from PIL import Image

MAX_RENDER_WIDTH = 3000
MAX_RENDER_HEIGHT = 3000

def to_pil(surface: cairo.ImageSurface) -> Image:
    format = surface.get_format()
    size = (surface.get_width(), surface.get_height())
    stride = surface.get_stride()

    with surface.get_data() as memory:
        if format == cairo.Format.RGB24:
            return Image.frombuffer(
                "RGB", size, memory.tobytes(),
                'raw', "BGRX", stride)
        elif format == cairo.Format.ARGB32:
            return Image.frombuffer(
                "RGBA", size, memory.tobytes(),
                'raw', "BGRa", stride)
        else:
            raise NotImplementedError(repr(format))

class Renderer:
    def __init__(self, pen_config, pen_mapping):
        super().__init__()
        self.pen_config = pen_config
        self.pen_mapping = pen_mapping
        self.render_data = None
        self.pil_image = None

    def get_rotated(self, rotation):
        img = []
        rot_img = self.pil_image.rotate(rotation)
        for i in range(0, rot_img.height):
            for j in range(0, rot_img.width):
                pixel = rot_img.getpixel((j, i))
                img.append(pixel[0]/255)
                img.append(pixel[1]/255)
                img.append(pixel[2]/255)
                img.append(1)

        return {"data": img, "height": rot_img.height, "width": rot_img.width}

    def set_scale_factor(self, width, height):
        self.scale = min(1, MAX_RENDER_WIDTH / width, MAX_RENDER_HEIGHT / height)

    def render(self, model: Model):
        bounding_box = model.get_bounding_box()

        width = bounding_box.max_x - bounding_box.min_x
        height = bounding_box.max_y - bounding_box.min_y
        self.set_scale_factor(width, height)
        h = math.ceil(height * self.scale)
        w = math.ceil(width * self.scale)

        data = numpy.zeros(shape=(h * w * 4), dtype=numpy.uint8)
        data = data.view(numpy.uint32).reshape((h, w))
        surface = cairo.ImageSurface.create_for_data(data, cairo.Format.ARGB32, w, h)

        self.ctx = cairo.Context(surface)
        self.ctx.save()
        self.ctx.set_source_rgba(1, 1, 1, 0.0)
        self.ctx.paint()
        self.ctx.restore()

        for line in model.lines:
            self.draw_line(line)

        data_view = data.view(numpy.uint8).reshape((h * w * 4)).astype(numpy.float32)
        data_view /= 255
        self.render_data = {"data": data_view, "height": h, "width": w}
        self.pil_image = to_pil(surface)
        return self.render_data

    def draw_line(self, line: Line):
        points = line.points
        if not len(points):
            return
        self.ctx.set_line_width(1)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.move_to(
            round(points[0].x * self.scale), round(points[0].y * self.scale)
        )
        for point in points:
            self.ctx.line_to(round(point.x * self.scale), round(point.y * self.scale))
        self.ctx.stroke()
