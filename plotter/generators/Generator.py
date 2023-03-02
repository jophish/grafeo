from abc import ABC, abstractmethod
from enum import Enum
from typing import TypedDict

from .Line import Line

# ParamList is a type for describing user-definable parameters for art generators
# ParamList maps param names to a tuple containing the param's shorthand code, description, and type
ParamType = str | int | float | bool
ParamList = dict[str, tuple[str, str, ParamType]]
ParamValues = dict[str, ParamType]


# The Generator class is the base class from which "art generators" inherit
# Each instance should ultimately generate ""
class Generator(ABC):
    lines: list[Line] = []
    param_list: ParamList = {}
    param_values: ParamValues = {}
    friendly_name: str

    def __init__(self):
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

    def get_friendly_name(self):
        return self.friendly_name

    def get_lines(self) -> list[Line]:
        if not self.lines:
            return None

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

    # Gets width, height of generated region
    @abstractmethod
    def get_dims(self) -> tuple[int, int]:
        pass
