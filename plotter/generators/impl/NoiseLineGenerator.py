from abc import ABC, abstractmethod
from py5 import Py5Vector
import random
import math
from plotter.utils.splines import generate_line, sample_spline
from ..Generator import Generator, GeneratorConfig, ParamList, ParamValues
from ..Line import Line, Pen

WIDTH = 16640
HEIGHT = 10720

class NoiseLineGenerator(Generator):

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

    def get_param_list(self) -> ParamList:
        return {
            'num_lines': ('nl', 'Number of lines to draw', int)
        }

    def get_default_params(self) -> ParamValues:
        return {
            'num_lines': 200
        }

    def generate_lines(self):
        # Use margin of 1000 units
        start_x = 1000
        start_y = 1000

        y_offsets = []

        # First, pick y offsets of each line
        cum_translation_y = 0
        num_lines = 200
        for i in range(num_lines):
            cum_translation_y += round(40 + random.randint(-20, 20) + 10*math.sin(i*(2*math.pi)/20))
            y_offsets.append(cum_translation_y)

        # We want to lerp into a new random line every so often. The frequency at which we change lines should
        # be irregular.
        num_unique_lines = 10
        unique_line_indices = sorted(random.sample(list(range(10,num_lines-10)), num_unique_lines - 2)) # Skip the first and last 10 so the boundaries are clean
        unique_line_indices = [0] + unique_line_indices + [num_lines-1]
        print(unique_line_indices)

        # Generate unique lines
        points_per_line = 50
        unique_lines = [
            generate_line(start_x, self.config['width'] - start_x*2, start_y, 50)
            for i in range(num_unique_lines)
        ]

        # Create a mapping of line indices to actual lines, and seed it with the unique lines
        line_map = {}
        for (index, line) in zip(unique_line_indices, unique_lines):
            line_map[index] = self.translate_line(line, 0, y_offsets[index])

        # For each line to draw, generate the actual line.
        current_unique_index = None
        next_unique_index = None
        for i in range(num_lines-1):
            # If we've already have a line saved, that means it's one of the "unique" lines, so set it as the current unique line
            # and set the next one to look at
            if i in line_map:
                current_unique_index = i
                next_unique_index = unique_line_indices[unique_line_indices.index(i) + 1]
                continue

            # If we haven't seen this line before, we want to lerp between the current unique index and the next one.
            fraction_till_next_line = (i - current_unique_index)/(next_unique_index - current_unique_index) # This will be the ratio for lerping
            lerped_line = self.lerp_lines(line_map[current_unique_index], line_map[next_unique_index], fraction_till_next_line)
            line_map[i] = lerped_line

        # Now, we have all of our lines. Turn them into splines!
        final_lines = []
        n_spine_samples = 1000
        for i in range(num_lines):
            final_lines.append(
                Line(sample_spline(line_map[i], 1000), Pen.ONE)
            )
        return final_lines

    def lerp_lines(self, line: list[Py5Vector], new_line: list[Py5Vector], ratio: float) -> list[Py5Vector]:
        lerped_line = []
        for (v1, v2) in zip(line, new_line):
            lerped_line.append(self.lerp_vectors(v1, v2, ratio))
        return lerped_line

    def lerp_vectors(self, v1: Py5Vector, v2: Py5Vector, ratio: float) -> Py5Vector:
        return v1.lerp(v2, ratio)

    def translate_line(self, line: list[Py5Vector], x_offset: int, y_offset: int) -> list[Py5Vector]:
        new_line = []
        for vector in line:
            new_line.append(
                Py5Vector(
                    vector.x + x_offset,
                    vector.y + y_offset
                )
            )
        return new_line
