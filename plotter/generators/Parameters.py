from abc import ABC
from enum import Enum, EnumType, StrEnum, auto
from typing import Generic, TypeVar


class ParamType(StrEnum):
    """The ParamType class is used to differentiate between parameter types."""

    Int = auto()
    Float = auto()
    Enum = auto()


T = TypeVar("T")


class GeneratorParam(ABC, Generic[T]):
    """
    GeneratorParam is the base class from which parameter types inherit.

    :ivar name: The name of this parameter
    :vartype name: str
    :ivar description: A human-readable description of this parameter
    :vartype description: str
    :ivar value: The current value of this parameter
    :vartype value: T
    :ivar default_value: The default value of this parameter
    :vartype value: T
    :ivar param_type: The type of this parameter
    :vartype value: :class:`ParamType`
    """

    def __init__(
        self, name: str, description: str, param_type: ParamType, default_value: T
    ):
        """
        Initialize a generator param.

        :param name: The name of this parameter
        :param description: A human-readable description of this parameter
        :param default_value: The default value of this parameter
        :param param_type: The type of this parameter
        """
        self.name: str = name
        self.description: str = description
        self.value: T = default_value
        self.default_value: T = default_value
        self.param_type: ParamType = param_type

    def reset(self):
        """Reset the parameter value to its default."""
        self.value = self.default_value


class IntParam(GeneratorParam[int]):
    """
    A parameter taking an integer value.

    :ivar min_value: The minimum value possible
    :vartype min_value: int
    :ivar max_value: The maximum value possible
    :vartype max_value: int
    """

    def __init__(
        self,
        name: str,
        description: str,
        default_value: int,
        min_value: int,
        max_value: int,
    ):
        """
        Initialize an integer generator param.

        :param name: The name of this parameter
        :param description: A human-readable description of this parameter
        :param default_value: The default value of this parameter
        :param min_value: The minimum value possible
        :param max_value: The maximum value possible
        """
        super().__init__(name, description, ParamType.Int, default_value)
        self.min_value: int = min_value
        self.max_value: int = max_value


class FloatParam(GeneratorParam[float]):
    """
    A parameter taking a float value.

    :ivar min_value: The minimum value possible
    :vartype min_value: float
    :ivar max_value: The maximum value possible
    :vartype max_value: float
    """

    min_value: float
    max_value: float

    def __init__(
        self,
        name: str,
        description: str,
        default_value: int,
        min_value: float,
        max_value: float,
    ):
        """
        Initialize a float generator param.

        :param name: The name of this parameter
        :param description: A human-readable description of this parameter
        :param default_value: The default value of this parameter
        :param min_value: The minimum value possible
        :param max_value: The maximum value possible
        """
        super().__init__(name, description, ParamType.Float, default_value)
        self.min_value: float = min_value
        self.max_value: float = max_value


class EnumParam(GeneratorParam[Enum]):
    """
    A parameter taking an enum value.

    :ivar options: The options to choose from
    :vartype options: :class:`EnumType`
    """

    def __init__(
        self, name: str, description: str, default_value: StrEnum, options: EnumType
    ):
        """
        Initialize an enum generator param.

        :param name: The name of this parameter
        :param description: A human-readable description of this parameter
        :param default_value: The default value of this parameter
        :param options: The options to choose from
        """
        super().__init__(name, description, ParamType.Enum, default_value)
        self.options: EnumType = options
