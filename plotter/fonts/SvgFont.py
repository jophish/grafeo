from pathlib import Path
from bs4 import BeautifulSoup
import bezier
import numpy as np
from plotter.models.Model import Model
from plotter.models.atoms.Line import Line
from plotter.models.atoms.Point import Point
from plotter.pens.Pen import Pen
from svg.path import parse_path
from svg.path import Path as SvgPath, Move as SvgMove, Close as SvgClose
from plotter.fonts.FontCharacter import FontCharacter
from plotter.fonts.FontFamily import FontFamily

def midpoint(point1, point2):
    return {
        'x': (point1['x'] + point2['x'])/2,
        'y': (point1['y'] + point2['y'])/2,
        'on': True
    }
    return [(x1 + x2)/2, (y1 + y2)/2]

# https://xmlgraphics.apache.org/batik/tools/font-converter.html

class SvgFont(FontFamily):
    """
    Wrapper class to turn SVG files into FontCharacter objects.
    """
    def __init__(self, svg_file_path, glyph_map):
        self.file_path = svg_file_path
        self.load_font()
        self.font_family = None
        self.glyph_map = glyph_map

        # Map from glyph names to FontCharacter
        self.font_character_map = {}

    def get_glyph_model(self, glyph_name):
        return self.get_font_character(glyph_name).model

    def get_text_model(self, lines):
        """
        Generate a model representing lines of text.

        Text is left-justified.
        """
        model = Model()
        y_offset = 0
        for line in lines:
            x_offset = 0
            row_model = Model()
            for char in line:
                glyph_map_key = f'{int(ord(char)):0{4}x}'.upper()
                glyph_name = self.glyph_map[glyph_map_key]
                font_char = self.get_font_character(glyph_name, char)
                char_model = font_char.model.copy()
                if not char_model.is_empty():
                    char_model.translate(x_offset, y_offset)
                    row_model.add_model(char_model)
                offset_to_use = font_char.x_offset if font_char.x_offset else self.x_offset
                x_offset += offset_to_use
            model.add_model(row_model)
            y_offset -= abs(self.ascent) + abs(self.descent)
        return model

    def load_font(self):
        self.font_xml = Path(self.file_path).read_bytes()
        self.font_tree = BeautifulSoup(self.font_xml, 'xml')

        font_face_node = self.font_tree.find('font-face')
        font_node = self.font_tree.find('font')

        self.ascent = float(font_face_node['ascent'])
        self.descent = float(font_face_node['descent'])
        self.x_offset = float(font_node['horiz-adv-x'])


    def get_font_character(self, glyph_name, char):
        if glyph_name in self.font_character_map:
            return self.font_character_map[glyph_name]

        glyph_node = self.font_tree.find('glyph', {'glyph-name': glyph_name})

        # Some fonts use non-standatrd glyph names. Try looking at the unicode
        # field instead.
        if not glyph_node:
            glyph_node = self.font_tree.find('glyph', {'unicode': char})

        model = Model()

        x_offset = None
        if glyph_node.has_attr('horiz-adv-x'):
            x_offset = float(glyph_node["horiz-adv-x"])

        # Probably looking at the char for "space"
        if not glyph_node.has_attr('d'):
            return FontCharacter(model, x_offset)

        path = parse_path(glyph_node['d'])

        paths = SvgFont.get_paths(path)

        num_samples = 150

        for path in paths:
            points = [path.point(i/num_samples) for i in range(num_samples + 1)]

            model.add_line(
                Line(
                    [
                        Point(float(point.real), float(point.imag), Pen.One) for point in points
                    ],
                    Pen.One
                )
            )

        self.font_character_map[glyph_name] = FontCharacter(model, x_offset)
        return self.font_character_map[glyph_name]

    @staticmethod
    def group_polygons(polygons):
        pass

    @staticmethod
    def get_paths(svg_path):
        lines = []
        current_line = []
        # Break up the path into separate "closed" sub-paths
        for component in svg_path:
            if type(component) == SvgMove:
                continue

            current_line.append(component)
            if type(component) == SvgClose:
                lines.append(current_line)
                current_line = []
        return [SvgPath(*line) for line in lines]


