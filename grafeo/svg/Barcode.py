from barcode.writer import BaseWriter
from ..models.Model import Model
from ..models.derived.Box import Box
from ..pens.Pen import Pen
import math

class BarcodeModelWriter(BaseWriter):

    def __init__(self, barcode_width, barcode_height, model_width, model_height):
        super().__init__(
            self.initialize.__get__(self),
            self.paint_module.__get__(self),
            self.paint_text.__get__(self),
            self.finish.__get__(self),
        )
        self.barcode_height_scale = .5
        self.barcode_width_scale = .9
        self.barcode_width = barcode_width*self.barcode_width_scale
        self.barcode_height = barcode_height*self.barcode_height_scale
        self.model_width = model_width
        self.model_height = model_height

        self.current_barcode = Model()

    def initialize(self, code):
        self.current_barcode = Model()

    def paint_module(self, xpos, ypos, width, color):
        if color == 'black':
            module_model = Box(width, self.module_height, xpos, ypos, Pen.One)
            module_model.hatch(Pen.One, 30.0, self.module_height/25)
            self.current_barcode.add_model(module_model)

    def paint_text(self, xpos, ypos):
        pass

    def finish(self):
        # Translate such that it's registered to origin
        bounding_box = self.current_barcode.get_bounding_box()
        min_x = bounding_box.min_x
        min_y = bounding_box.min_y
        current_width = bounding_box.max_x - bounding_box.min_x
        current_height = bounding_box.max_y - bounding_box.min_y

        self.current_barcode.translate(-min_x, -min_y)
        self.current_barcode.apply_matrix([
            [self.barcode_width/current_width, 0],
            [0, self.barcode_height/current_height]
        ])

        self.current_barcode.translate((1-self.barcode_width_scale)*self.barcode_width/2, self.model_height + (1-self.barcode_height_scale)*self.barcode_height)

        return self.current_barcode


class BarcodeModelWriter2(BaseWriter):

    def __init__(self, origin_x, origin_y, width, height, rot):
        super().__init__(
            self.initialize.__get__(self),
            self.paint_module.__get__(self),
            self.paint_text.__get__(self),
            self.finish.__get__(self),
        )

        self.barcode_height_scale = .5
        self.barcode_width_scale = .9
        self.width = width
        self.height = height
        self.barcode_width = width * self.barcode_width_scale
        self.barcode_height = height * self.barcode_height_scale
        self.rot = rot

        self.origin_x = origin_x
        self.origin_y = origin_y

        self.current_barcode = Model()

    def initialize(self, code):
        self.current_barcode = Model()

    def paint_module(self, xpos, ypos, width, color):
        if color == 'black':
            module_model = Box(width, self.module_height, xpos, ypos, Pen.One)
            module_model.hatch(Pen.One, 30.0, self.module_height/50)
            self.current_barcode.add_model(module_model)

    def paint_text(self, xpos, ypos):
        pass

    def finish(self):
        # Translate such that it's centered about origin
        bounding_box = self.current_barcode.get_bounding_box()
        min_x = bounding_box.min_x
        min_y = bounding_box.min_y
        current_width = bounding_box.max_x - bounding_box.min_x
        current_height = bounding_box.max_y - bounding_box.min_y

        self.current_barcode.translate(-min_x - current_width/2, -min_y - current_height/2)
        self.current_barcode.apply_matrix([
            [self.barcode_width/current_width, 0],
            [0, self.barcode_height/current_height]
        ])

        bounding_box = self.current_barcode.get_bounding_box()
        # Now we're scaled correctly, rotate about origin.
        self.current_barcode.rotate(self.rot, 0, 0)

        barcode_origin_x = bounding_box.min_x*math.cos(math.pi*self.rot/180.0) - bounding_box.min_y*math.sin(math.pi*self.rot/180.0)
        barcode_origin_y = bounding_box.min_y*math.cos(math.pi*self.rot/180.0) + bounding_box.min_x*math.sin(math.pi*self.rot/180.0)

        self.current_barcode.translate(self.origin_x - barcode_origin_x, self.origin_y - barcode_origin_y)

        return self.current_barcode
