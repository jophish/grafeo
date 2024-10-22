import os
import xml.etree.ElementTree as ET
from pathlib import Path
from plotter.fonts.TrueType import TrueType
from plotter.fonts.SvgFont import SvgFont


glyph_map_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aglfn.txt')
ttx_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ttf/')
svg_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'svg/')

class Singleton(object):
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(Singleton, cls).__new__(cls)
    return cls.instance

class FontManager(Singleton):
    def __init__(self):
        # Map from unicode chars to glyph names
        self.glyph_map = {}
        # Map from font names to FontFamily objects
        self.font_map = {}

        self.load_glyph_map()
        self.load_font_map()

    def get_fonts(self):
        return list(self.font_map.keys())

    def load_glyph_map(self):
        with open(glyph_map_file_path, 'r') as f:
            lines = list(filter(lambda line: not line.startswith("#"), [line.rstrip() for line in f]))
            for line in lines:
                parts = line.split(';')
                self.glyph_map[parts[0]] = parts[1]

    def load_font_map(self):
        for file_name in os.listdir(svg_dir_path):
            font_name = file_name.split('.')[0]
            self.font_map[font_name] = SvgFont(os.path.join(svg_dir_path, file_name), self.glyph_map)

    def get_font_family(self, font_name):
        return self.font_map[font_name]

