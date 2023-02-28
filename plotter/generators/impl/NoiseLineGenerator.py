from abc import ABC, abstractmethod
from py5 import Py5Vector
import random
import math
from plotter.utils.splines import generate_line, sample_spline
from ..Generator import Generator, ParamList, ParamValues
from ..Line import Line
from plotter.utils.hatch import hatch_lines

class NoiseLineGenerator(Generator):

    friendly_name = 'noisy lines'

    @classmethod
    def get_friendly_name(cls):
        return cls.friendly_name

    def __init__(self):
        self.config = {
            'width': 16640,
            'height': 10720
        }
        super().__init__()

    def get_param_list(self) -> ParamList:
        return {
            'num_lines': ('nl', 'Number of lines to draw', 'int', 5, 1000),
            'num_unique_lines': ('nul', 'Number of unique lines to lerp between', 'int', 0, 200),
            'unique_line_placement_strategy': ('ulps', 'Strategy to use for placing unique lines vertically.', 'enum', ['RAND', 'UNIFORM']),
            'line_distance': ('ld', 'Base distance between consecutive lines', 'int', 0, 500),
            'line_distance_rand_amp': ('ldra', 'Amplitude of randomness added to distance between consecutive lines', 'int', 0, 500),
            'line_distance_sin_amp': ('ldsa', 'Amplitude of sin added to distance between consecutive lines', 'int', 0, 500),
            'num_control_points': ('ncp', 'Number of control points to use for each line', 'int', 0, 1000),
            'start_x': ('sx', 'Starting location on x axis for drawing lines', 'int', 0, 16640),
            'start_y': ('sy', 'Starting location on y axis for drawing lines (ending location depends on number of lines)', 'int', 0, 10720),
            'end_x': ('ex', 'Ending location on x axis for drawing lines (as distance from border of region)', 'int', 0, 16640),
            'num_spline_samples': ('nss', 'Number of samples per spline', 'int', 1, 5000),
            'spline_tightness': ('st', '"Tightness" parameter for spline generation', 'int', -1000, 1000),
            'line_x_sin_amp': ('lxsa', 'Amplitude of sinusoidal variation for x component of line generation', 'float', 0, 1000),
            'line_x_sin_freq': ('lxsf', 'Frequency of sinusoidal variation for x component of line generation', 'float', 0, 1000),
            'line_x_rand_amp': ('lxra', 'Amplitude of random variation for x component of line generation', 'float', 0, 1000),
            'line_x_sin_amp_exp': ('lxsae', 'Exponential factor for amplitude of sinusoidal variation for x component of line generation', 'float', 0, 10),
            'line_x_sin_freq_exp': ('lxsfe', 'Exponential factor for frequency of sinusoidal variation for x component of line generation', 'float', 0, 10),
            'line_x_rand_amp_exp': ('lxrae', 'Exponential factor for amplitude of random variation for x component of line generation', 'float', 0, 10),
            'line_y_sin_amp': ('lysa', 'Amplitude of sinusoidal variation for y component of line generation', 'float', 0, 1000),
            'line_y_sin_freq': ('lysf', 'Frequency of sinusoidal variation for y component of line generation', 'float', 0, 1000),
            'line_y_rand_amp': ('lyra', 'Amplitude of random variation for y component of line generation', 'float', 0, 1000),
            'line_y_sin_amp_exp': ('lysae', 'Exponential factor for amplitude of sinusoidal variation for y component of line generation', 'float', 0, 10),
            'line_y_sin_freq_exp': ('lysfe', 'Exponential factor for frequency of sinusoidal variation for y component of line generation', 'float', 0, 10),
            'line_y_rand_amp_exp': ('lyrae', 'Exponential factor for amplitude of random variation for y component of line generation', 'float', 0, 10),
        }

    def get_default_params(self) -> ParamValues:
        return {
            'num_lines': 200,
            'num_unique_lines': 5,
            'unique_line_placement_strategy': 'UNIFORM',
            'line_distance': 30,
            'line_distance_rand_amp': 30,
            'line_distance_sin_amp': 10,
            'num_control_points': 50,
            'start_x': 1000,
            'start_y': 2000,
            'end_x': 1800,
            'num_spline_samples': 1000,
            'spline_tightness': 0,
            'line_x_sin_amp': 100,
            'line_x_sin_freq': 50,
            'line_x_rand_amp': 50,
            'line_x_sin_amp_exp': .4,
            'line_x_sin_freq_exp': .4,
            'line_x_rand_amp_exp': .4,
            'line_y_sin_amp': 100,
            'line_y_sin_freq': 50,
            'line_y_rand_amp': 50,
            'line_y_sin_amp_exp': .4,
            'line_y_sin_freq_exp': .2,
            'line_y_rand_amp_exp': .4
        }

    def generate_lines(self, **kwargs):
        # Define margins
        start_x = kwargs['start_x']
        start_y = kwargs['start_y']

        y_offsets = []

        # First, pick y offsets of each line
        cum_translation_y = 0
        num_lines = kwargs['num_lines']

        line_distance = kwargs['line_distance']
        line_distance_rand_amp = kwargs['line_distance_rand_amp']
        for i in range(num_lines):
            cum_translation_y += round(line_distance + random.randint(-line_distance_rand_amp, line_distance_rand_amp) + kwargs['line_distance_sin_amp']*math.sin(i*(2*math.pi)/20))
            y_offsets.append(cum_translation_y)

        # We want to lerp into a new random line every so often. We have different strategies for choosing where to place these lines.
        num_unique_lines = kwargs['num_unique_lines']
        unique_line_placement_strategy = kwargs['unique_line_placement_strategy']
        unique_line_indices = []
        if unique_line_placement_strategy == 'UNIFORM':
            lines_per_unique = num_lines/(num_unique_lines + 1)
            unique_line_indices = [round(i*lines_per_unique) for i in range(1,num_unique_lines+1)]
        elif unique_line_placement_strategy == 'RAND':
            unique_line_indices = sorted(random.sample(list(range(num_lines)), num_unique_lines))
        else:
            raise Exception(f'Unknown line placement strategy "{unique_line_placement_strategy}"')
        unique_line_indices = [0] + unique_line_indices + [num_lines-1]


        # Generate unique lines
        points_per_line = kwargs['num_control_points']
        unique_lines = [
            generate_line(
                start_x,
                self.config['width'] - kwargs['end_x'],
                start_y,
                points_per_line,
                x_sin_amp=kwargs['line_x_sin_amp'],
                x_sin_freq=kwargs['line_x_sin_freq'],
                x_rand_amp=kwargs['line_x_rand_amp'],
                x_sin_amp_exp=kwargs['line_x_sin_amp_exp'],
                x_sin_freq_exp=kwargs['line_x_sin_freq_exp'],
                x_rand_amp_exp=kwargs['line_x_rand_amp_exp'],
                y_sin_amp=kwargs['line_y_sin_amp'],
                y_sin_freq=kwargs['line_y_sin_freq'],
                y_rand_amp=kwargs['line_y_rand_amp'],
                y_sin_amp_exp=kwargs['line_y_sin_amp_exp'],
                y_sin_freq_exp=kwargs['line_y_sin_freq_exp'],
                y_rand_amp_exp=kwargs['line_y_rand_amp_exp'],
            )
            for i in range(num_unique_lines + 2) # Add two for start/end
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
            fraction_till_next_line = (y_offsets[i] - y_offsets[current_unique_index])/(
                y_offsets[next_unique_index] - y_offsets[current_unique_index]) # This will be the ratio for lerping

            lerped_line = self.lerp_lines(line_map[current_unique_index], line_map[next_unique_index], fraction_till_next_line)
            line_map[i] = lerped_line

        num_diff_pens = 8
        # Now, we have all of our lines. Turn them into splines!
        final_lines = []
        n_spine_samples = kwargs['num_spline_samples']
        for i in range(num_lines):
            line = self.filter_oob(sample_spline(line_map[i], 1000, kwargs['spline_tightness']))
            pen_num = 0
            final_lines.append(Line(line, pen_num))


        return final_lines

    def filter_oob(self, line: list[Py5Vector]) -> list[Py5Vector]:
        new_line = []
        for v in line:
            if v.x < 0 or v.x >= self.config['width'] or v.y < 0 or v.y > self.config['height']:
                continue
            new_line.append(v)
        return new_line

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
