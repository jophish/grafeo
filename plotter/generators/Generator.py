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

# The Generator class is the base class from which "art generators" inherit
# Each instance should ultimately generate ""
class Generator(ABC):

    lines: list[Line] = []
    param_list: ParamList = {}
    param_values: ParamValues = {}
    config: GeneratorConfig

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.param_list = self.get_param_list()
        self.reset_params()

    def generate(self):
        self.lines = self.generate_lines(**self.params)
        return self.lines

    # Resets parameter values to defaults
    def reset_params(self):
        self.param_values = self.get_default_params()

    # Returns the current parameter values
    def get_param_list(self) -> ParamList:
        return self.param_list

    # Sets the parameter with the given name to the given value
    def set_param(self, param_name: str, param_value: ParamType):
        self.param_values[param_name] = param_value

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
        if len(self.gpgl):
            return self.gpgl

        self.gpgl.append('H')
        for line in self.lines:
            for i in range(len(line)):
                if i == 0:
                    self.gpgl.append(f'M{round(line[i].x)},{round(line[i].y)}')
                self.gpgl.append(f'D{round(line[i].x)},{round(line[i].y)}')

        return self.gpgl
