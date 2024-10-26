from pathlib import Path
from bs4 import BeautifulSoup
from plotter.svg.Svg import Svg
import math
from plotter.models.atoms.Line import Line
from plotter.models.atoms.Point import Point
from plotter.models.Model import Model
from plotter.pens.Pen import Pen

def make_registration_mark_model(size, bounding_box, height, width, duplicate_times):
    mark_model = Model()
    mark_model.add_line(Line(
        [
            Point(size/2, size/4, Pen.One),
            Point(size/2, size*3/4, Pen.One),
        ],
        Pen.One
    ))
    mark_model.add_line(Line(
        [
            Point(size/4, size/2, Pen.One),
            Point(size*3/4, size/2, Pen.One),
        ],
        Pen.One
    ))
    top_left = mark_model.copy()
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
              # TODO: Not adding registration marks results in bad spacing
                if self._show_registration_marks or True:
                    duplicate_times = 1
                    if i == 0 and j == 0:
                        duplicate_times = 2 # This is a hack to counteract pen dryness
                    current_model = self._add_registration_marks(current_model, duplicate_times)
                bounding_box = current_model.get_bounding_box()

                current_model.translate(
                    -bounding_box.min_x + j*(self.width+self._registration_mark_size*2),
                    -bounding_box.min_y + (self.num_rows - 1 - i)*(self.height+self._registration_mark_size*2))

                page_model.add_model(current_model)

        self.page_map[page] = page_model
        return page_model

    def _add_registration_marks(self, model, duplicate_times):
        # Assumes model is registered to the origin
        mark_model = make_registration_mark_model(self._registration_mark_size, model.get_bounding_box(), self.height, self.width, duplicate_times)
        new_model = model.copy()
        new_model.add_model(mark_model, True)
        return new_model

