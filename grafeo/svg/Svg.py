from svg.path import parse_path
from ..models.Model import Model
from ..models.atoms.Line import Line
from ..models.atoms.Point import Point
from ..pens.Pen import Pen
from svg.path import Line as SvgLine

class Svg():

    def __init__(self, paths, width, height):
        self.paths = paths
        self.width = width
        self.height = height
        self.model = None

    def get_model(self):
        if self.model:
            return self.model
        else:
            model = Model()
            for raw_path in self.paths:
                # This is a beautifulsoup node
                path = parse_path(raw_path['d'])
                line_points = []
                for i in range(len(path)):
                    element = path[i]
                    if type(element) == SvgLine:
                        if i == 0:
                            line_points.append(
                                Point(float(element.start.real), float(-element.start.imag + self.height), Pen.One),
                            )
                        line_points.append(
                            Point(float(element.end.real), float(-element.end.imag + self.height), Pen.One),
                        )
                line = Line(line_points, Pen.One)
                model.add_line(line)
            self.model = model
            return model
