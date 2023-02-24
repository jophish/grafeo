from abc import ABC, abstractmethod
from .Line import Line
from enum import Enum
from typing import TypedDict

# ParamList is a type for describing user-definable parameters for art generators
# ParamList maps param names to a tuple containing the param's shorthand code, description, and type
ParamType = str | int | float | bool
ParamList = dict[str, tuple[str, str, ParamType]]
ParamValues = dict[str, ParamType]

class GeneratorConfig(TypedDict):
    width: int
    height: int
    scale: float

# The Generator class is the base class from which "art generators" inherit
# Each instance should ultimately generate ""
class Generator(ABC):


    lines: list[Line] = []
    param_list: ParamList = {}
    param_values: ParamValues = {}
    config: GeneratorConfig
    name: str

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.param_list = self.get_param_list()
        self.reset_params()

    def generate(self):
        self.lines = self.generate_lines(**self.param_values)
        return self.lines

    # Resets parameter values to defaults
    def reset_params(self):
        self.param_values = self.get_default_params()

    # Returns the current parameter values
    def get_param_values(self) -> ParamValues:
        return self.param_values

    # Sets the parameter with the given name to the given value
    def set_param_value(self, param_name: str, param_value: ParamType):
        self.param_values[param_name] = param_value

    def set_param_values(self, param_values: ParamValues):
        self.param_values = param_values

    def get_name(self):
        return self.name

    def get_lines(self) -> list[Line]:
        return self.lines

    # Main method for line generation
    @abstractmethod
    def generate_lines(self, **kwargs):
        pass

    # Gets the default parameters for this Generator
    @abstractmethod
    def get_default_params(self) -> ParamValues:
        pass

    # Gets information describing the parameters accepted by this Generator
    @abstractmethod
    def get_param_list(self) -> ParamList:
        pass


    def generate_gpgl(self):
        if len(self.lines) == 0:
            return None

        gpgl = []
        gpgl.append('H')

        for line in self.lines:
            points = line.get_points()
            for i in range(len(points)):
                if i == 0:
                    # Using the y-component as-is results in a mirrored image about the horizontal axis;
                    # flip it here...
                    gpgl.append(f'M{round(points[i].x)},{self.config["height"]-round(points[i].y)}')
                gpgl.append(f'D{round(points[i].x)},{self.config["height"]-round(points[i].y)}')

        return gpgl
