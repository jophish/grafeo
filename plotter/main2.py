from .models.Model import Model
from .models.atoms.Line import Line
from .models.atoms.Point import Point
from .pens.Pen import Pen

pen = Pen.ONE
model = Model()
points = [Point(0, 0, pen), Point(1, 2, pen)]
line = Line(points, pen)
model.add_line(line)

lerped_point = points[0].lerp(points[1], .5)
print(lerped_point.x, lerped_point.y)
