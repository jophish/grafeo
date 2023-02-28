from plotter.generators.Line import Line
import io
import numpy
import cairo
import array



class Renderer():
    def __init__(self, pen_config,  pen_mapping):
        super().__init__()
        self.pen_config = pen_config
        self.pen_mapping = pen_mapping

    def set_lines(self, lines: list[Line]):
        self.lines = lines

    def setup(self):
        pg = self.create_graphics(16640, 10720) # Generators need to define width/height and expose it somehow
        pg.begin_draw()
        pg.background(255, 255, 255)
        for line in self.lines:
            shape = self.make_shape_from_line(line)
            pg.shape(shape)
        pg.end_draw()
        pg.load_np_pixels()
        # self.pixels = numpy.moveaxis(self.pg.np_pixels, [0, 1, 2, 3], [3, 0, 1 , 2])
        self.pixels = pg.np_pixels/255.0
        self.exit_sketch()


    def render(self, lines: list[Line]):
        h = 10720
        w =  16640
        #data = numpy.zeros((h, w, 4), dtype=numpy.uint8)
        data = numpy.zeros(shape=(h*w*4), dtype=numpy.uint8)
        data = data.view(numpy.uint32).reshape((h, w))

        surface = cairo.ImageSurface.create_for_data(data, cairo.Format.ARGB32, h, w)
        self.ctx = cairo.Context(surface)

        self.ctx.save()
        self.ctx.set_source_rgb(1, 1, 1);
        self.ctx.paint()
        self.ctx.restore()
        for line in lines:
            continue
            self.draw_line(line)

        data_view = data.view(numpy.uint8).reshape((h*w*4)).astype(numpy.float64)
        data_view /= 255
        return array.array('f', data_view.tolist())

    def draw_line(self, line):
        points = line.get_points()
        self.ctx.move_to(points[0].x, points[0].y)
        for point in points:
            self.ctx.line_to(point.x, point.y)
        self.ctx.stroke()


    def make_shape_from_line(self, line: Line):
        s = self.create_shape()
        s.begin_shape()
        for vector in line.get_points():
            s.vertex(vector.x, vector.y)
        s.end_shape()
        s.set_fill(False)

        # pen = self.pens[str(line.get_pen_num())]
        # s.set_stroke_weight(pen['weight'])
        # s.set_stroke(pen['color'])
        s.set_stroke_weight(30)
        s.set_stroke('#000000')
        return s
