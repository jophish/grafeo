from pathlib import Path
from bs4 import BeautifulSoup
from ..models.Model import Model
from ..models.atoms.Line import Line
from ..models.atoms.Point import Point
from ..pens.Pen import Pen
from svg.path import parse_path
from svg.path import Path as SvgPath, Move as SvgMove, Close as SvgClose
from ..fonts.FontCharacter import FontCharacter
from ..fonts.FontFamily import FontFamily
from ..models.derived.Polygon import Polygon
from ..models.derived.MultiPolygon import MultiPolygon
import networkx as nx


def midpoint(point1, point2):
    return {
        'x': (point1['x'] + point2['x'])/2,
        'y': (point1['y'] + point2['y'])/2,
        'on': True
    }
    return [(x1 + x2)/2, (y1 + y2)/2]


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

    def get_text_model(self, lines, hatch_angle, hatch_spacing):
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
                    if hatch_angle and hatch_spacing:
                        char_model.hatch(Pen.One, hatch_angle, hatch_spacing)
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

        # If we can't find the glyph... assume it's a space. This is sometimes right, actually.
        if not glyph_node:
            return FontCharacter(MultiPolygon([], Pen.One), self.x_offset)

        x_offset = None
        if glyph_node.has_attr('horiz-adv-x'):
            x_offset = float(glyph_node["horiz-adv-x"])

        # Probably looking at the char for "space"
        if not glyph_node.has_attr('d'):
            return FontCharacter(MultiPolygon([], Pen.One), x_offset)

        path = parse_path(glyph_node['d'])

        paths = SvgFont.get_paths(path)

        num_samples = 150

        polygons = []
        for path in paths:
            points = [path.point(i/num_samples) for i in range(num_samples + 1)]

            polygons.append(Polygon(
                Line(
                    [
                        Point(float(point.real), float(point.imag), Pen.One) for point in points
                    ],
                    Pen.One
                ),
                Pen.One
            ))

        polygon_groups = SvgFont.group_polygons(polygons)
        polygons_with_holes = []
        for poly, holes in polygon_groups.items():
            hole_lines = [polygons[hole_index].lines[0] for hole_index in holes]
            polygons_with_holes.append(
                Polygon(
                    polygons[poly].lines[0],
                    Pen.One,
                    hole_lines
                )
            )

        model = MultiPolygon(polygons_with_holes, Pen.One)
        self.font_character_map[glyph_name] = FontCharacter(model, x_offset)
        return self.font_character_map[glyph_name]

    @staticmethod
    def group_polygons(polygons):
        # We need to create a directed graph of "contained-ness" for polygons.
        graph = nx.DiGraph()
        graph.add_nodes_from(range(len(polygons)))
        for i in range(len(polygons)):
            graph.nodes[i]['status'] = None

        for i in range(len(polygons)):
            for j in range(len(polygons)):
                if i == j:
                    continue
                if polygons[i].contains(polygons[j]):
                    graph.add_edge(i, j)

        # These are our intial base polygons. These act as roots of trees.
        start_polygons = [res[0] for res in graph.in_degree(range(len(polygons))) if res[1] == 0]
        # A map from polygons to holes within polygon
        polygon_hole_map = {i: [] for i in range(len(polygons))}

        # Now, for each base polygon, traverse the graph.
        while len(start_polygons) > 0:
            node = start_polygons.pop(0)
            if graph.in_degree(node) == 0:
                graph.nodes[node]['status'] = 'solid'
            else:
                # Look at the predecessors of this node. If some are not yet known, we'll come
                # back to this later. If there are an equal number of solid and holes, this must be solid.
                # If there are more solids than holes, this must be a hole. If it is a hole, it will belong
                # to the solid predecessor with the greatest in-degree
                predecessor_statuses = [(i, graph.nodes[i]['status']) for i in graph.predecessors(node)]
                if None in predecessor_statuses:
                    start_polygons.append(node)

                statuses = [status[1] for status in predecessor_statuses]
                solid_count = statuses.count('solid')
                hole_count = statuses.count('hole')

                if (solid_count <= hole_count):
                    graph.nodes[node]['status'] = 'solid'
                else:
                    graph.nodes[node]['status'] = 'hole'
                    # Get the poly to which this hole belongs
                    solid_predecessors = [status[0] for status in predecessor_statuses if status[1] == 'solid']
                    in_degrees = graph.in_degree(solid_predecessors)
                    parent = max(in_degrees, key = lambda x: x[1])
                    polygon_hole_map[parent[0]].append(node)
                    del polygon_hole_map[node]

            # Sort successors by in-degree, lowest to highest. Higher in-degree means greater depth,
            # which means the node is contained within many other nodes.
            successors = graph.successors(node)
            for successor in successors:
                start_polygons.insert(0, successor)

        return polygon_hole_map

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


