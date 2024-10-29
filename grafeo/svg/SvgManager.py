from pathlib import Path
from bs4 import BeautifulSoup
from .Svg import Svg
import math
from ..models.atoms.Line import Line
from ..models.atoms.Point import Point
from ..models.Model import Model
from ..pens.Pen import Pen
from ..models.derived.Box import Box
from .Barcode import BarcodeModelWriter
from barcode import Code39
from ..fonts.FontManager import FontManager
from ..utils.scaling import scale_to_fit

def make_registration_mark_model(size, bounding_box, height, width, duplicate_times):
    mark_model = Model()
    mark_model.add_line(Line(
        [
            Point(size/2, 0, Pen.One),
            Point(size/2, size, Pen.One),
        ],
        Pen.One
    ))
    mark_model.add_line(Line(
        [
            Point(0, size/2, Pen.One),
            Point(size, size/2, Pen.One),
        ],
        Pen.One
    ))

    # The top left corner has an additional mark for orientation
    top_left = mark_model.copy()
    top_left_box = Box(size/4, size/4, size/8, size*7.0/8.0, Pen.One)

    top_left.add_model(top_left_box)
    top_left.translate(-size, height)

    top_right = mark_model.copy()
    top_right.translate(width, height)
    bottom_right = mark_model.copy()
    bottom_right.translate(width, -size)
    bottom_left = mark_model.copy()
    bottom_left.translate(-size, -size)
    model = Model()
    for i in range(duplicate_times):
        model.add_model(top_left.copy())
        model.add_model(top_right.copy())
        model.add_model(bottom_right.copy())
        model.add_model(bottom_left.copy())
    return model

class SvgManager():

    def __init__(self):
        self.multi_frame = False
        self.svgs = []
        self.num_rows = 1
        self.num_cols = 1
        # Map from page number to model representing page to print
        self.page_map = {}
        self.pages = 0
        self._show_registration_marks = False
        self._registration_mark_size = 10
        self.current_page = 0

    def _update_page_map(self):
        self.page_map = {}
        self.current_page = 0
        self.pages = math.ceil(len(self.svgs) / (self.num_rows * self.num_cols))

    def show_registration_marks(self, value):
        self._show_registration_marks = value
        self._update_page_map()

    def set_registration_mark_size(self, size):
        self._registration_mark_size = size
        self._update_page_map()

    def set_current_page(self, page):
        self.current_page = page

    def update_num_rows(self, num_rows):
        self.num_rows = num_rows
        if self.svgs:
            self._update_page_map()

    def update_num_cols(self, num_cols):
        self.num_cols = num_cols
        if self.svgs:
            self._update_page_map()

    def load_svg(self, file_path):
        """
        Load an SVG from a file path.

        Currently, this only supports multi-frame SVGs for the purposes of animation.
        In particular, the exact output of Blender's Freestyle SVG plugin.
        """
        self.file_path = file_path
        self.svg_xml = Path(self.file_path).read_bytes()
        self.svg_tree = BeautifulSoup(self.svg_xml, 'xml')
        svg_node = self.svg_tree.find('svg')

        self.width = float(svg_node['width'])
        self.height = float(svg_node['height'])

        frames = self.svg_tree.findAll('g', id='strokes')
        self.svgs = [self._make_svg_from_frame(frame) for frame in frames]

        self._update_page_map()

    def _make_svg_from_frame(self, frame):
        paths = frame.findAll('path')
        return Svg(paths, self.width, self.height)

    def get_num_pages(self):
        return self.pages

    def get_model_for_current_page(self):
        return self.get_model_for_page(self.current_page)

    def get_model_for_page(self, page):
        if len(self.svgs) == 0:
            return Model()

        if page in self.page_map:
            return self.page_map[page]

        font_manager = FontManager()

        models_per_page = self.num_rows * self.num_cols
        # TODO: IDK if we need this copy
        models = [svg.get_model().copy() for svg in self.svgs[models_per_page*page:models_per_page*(page+1)]]
        page_model = Model()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                index = i * self.num_rows + j

                # This model will always be registered to the origin in page space
                current_model = Model()
                # This may happen on the final page
                if (index) < len(models):
                    current_model = models[index]

                # Make the registration marks
                current_model = self._add_registration_marks(current_model, 1)
                bounding_box = current_model.get_bounding_box()

                # Make the machine readable barcode
                frame_num = page*models_per_page + (index+1)
                code = f'W{int(self.width)}H{int(self.height)}F{frame_num}'
                # IDEA: Generate 3 barcodes; one each for height, width, and frame number, and use different edges for each.
                barcode = Code39(code, writer=BarcodeModelWriter(self.width, self._registration_mark_size, self.width, self.height))
                barcode_model = barcode.render()
                current_model.add_model(barcode_model)

                # Make the human-readable metadata
                code_rows = [[char] for char in code]
                font_family = font_manager.get_font_family('SourceCodePro-Regular')
                text_model = font_family.get_text_model(code_rows, None, None)
                text_model_bounding_box = text_model.get_bounding_box()
                text_model.translate(-text_model_bounding_box.min_x, -text_model_bounding_box.min_y)

                # Scale the text so that the width fits within the margins, less some scaling factor
                height_scale = .95
                text_current_width = text_model_bounding_box.max_x - text_model_bounding_box.min_x
                text_current_height = text_model_bounding_box.max_y - text_model_bounding_box.min_y
                (scaled_x, scaled_y) = scale_to_fit(
                    text_current_width, text_current_height,
                    self._registration_mark_size*.5, self.height*height_scale,
                )
                text_scale_factor = scaled_x / text_current_width
                text_model.apply_matrix([
                    [text_scale_factor, 0],
                    [0, text_scale_factor]
                ])
                # Translate the text such that the top left corner is near the bottom of the top left registration mark
                text_model_bounding_box = text_model.get_bounding_box()
                text_height = text_model_bounding_box.max_y - text_model_bounding_box.min_y
                text_width = text_model_bounding_box.max_x - text_model_bounding_box.min_x
                translate_text_x = -self._registration_mark_size + self._registration_mark_size/2 - text_width/2
                translate_text_y = self.height*(height_scale + (1 - height_scale)/2) - text_height
                #text_model.translate(-text_model_bounding_box.min_x, -text_model_bounding_box.min_y)
                text_model.translate(-text_model_bounding_box.min_x + translate_text_x, -text_model_bounding_box.min_y + translate_text_y)
                current_model.add_model(text_model)

                # Make the margins
                margin_size = self._registration_mark_size * .25
                margin_box = Box(
                    self.width+ self._registration_mark_size*2 + margin_size*2,
                    self.height + self._registration_mark_size*2 + margin_size*2,
                    bounding_box.min_x - margin_size,
                    bounding_box.max_y + margin_size,
                    Pen.One
                )
                current_model.add_model(margin_box, True)

                
                bounding_box = current_model.get_bounding_box()
                current_model.translate(
                    -bounding_box.min_x + j*(self.width+self._registration_mark_size*2 + margin_size*2),
                    -bounding_box.min_y + (self.num_rows - 1 - i)*(self.height+self._registration_mark_size*2 + margin_size*2))

                page_model.add_model(current_model)

        self.page_map[page] = page_model
        return page_model

    def _add_registration_marks(self, model, duplicate_times):
        # Assumes model is registered to the origin
        mark_model = make_registration_mark_model(self._registration_mark_size, model.get_bounding_box(), self.height, self.width, duplicate_times)
        new_model = model.copy()
        new_model.add_model(mark_model, True)
        return new_model

