from abc import ABC, abstractmethod
from py5 import Py5Vector
import random
import math
from plotter.utils.splines import generate_line, sample_spline
from ..Generator import Generator, ParamList, ParamValues
from ..Line import Line
from plotter.utils.hatch import hatch_lines

class Test(Generator):

    friendly_name = 'testing'

    @classmethod
    def get_friendly_name(cls):
        return cls.friendly_name

    def __init__(self):
        super().__init__()

    def get_dims(self):
        return (1000, 1000)

    def get_param_list(self) -> ParamList:
        return {
            'num_lines': ('nl', 'Number of lines to draw', 'int', 5, 1000),
            'num_unique_lines': ('nul', 'Number of unique lines to lerp between', 'int', 0, 200),
            'unique_line_placement_strategy': ('ulps', 'Strategy to use for placing unique lines vertically.', 'enum', ['RAND', 'UNIFORM']),
        }

    def get_default_params(self) -> ParamValues:
        return {
            'num_lines': 200,
            'num_unique_lines': 5,
            'unique_line_placement_strategy': 'UNIFORM',
        }

    def generate_lines(self, **kwargs):
        return []
