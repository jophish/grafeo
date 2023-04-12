from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum
from typing import Any, Generic, TypeVar, Union


class ParamNotFoundException(Exception):
    """Exception raised when parameter is not found."""

    pass


class WrongParamTypeException(Exception):
    """Exception raised when wrong parameter type is used."""

    pass


class InvalidParamValueException(Exception):
    """Exception raised when a parameter value is invalid."""

    pass


class ParamType(Enum):
    """The ParamType class is used to differentiate between parameter types."""

    Int = int
    Float = float
    Enum = str


T = TypeVar("T")


class GeneratorParamGroup:
    """
    GeneratorParamGroup is a logical container for an ordered group of generator parameters.

    A parameter group can consist of both lone parameters as well as sub-groups.

    :ivar name: The name of this parameter group
    :vartype name: str
    :ivar params: A mapping from param name to param object
    :vartype params: :class:`OrderedDict`[str, :class:`GeneratorParams` | :class:`GeneratorParamGroup`]
    """

    def __init__(
        self, name: str, params: list[Union["GeneratorParam", "GeneratorParamGroup"]]
    ):
        """
        Initialize a param group.

        :param name: The name of this parameter group
        :param generator_params: The parameters or subgroups in this group
        """
        self.name: str = name
        self.params: OrderedDict[
            str, GeneratorParam | "GeneratorParamGroup"
        ] = OrderedDict([(param.name, param) for param in params])

    def reset(self):
        """Reset all parameter values to their default."""
        for param in self.params.values():
            param.reset()

    def get_dict_values(self) -> dict[str, Any]:
        """
        Return a nested dictionary containing the current parameter values.

        The output of this method returns a shape compatible with `set_dict_values`.

        :return: Nested dictionary containing parameter values
        """
        param_dict = {}
        for name, param in self.params.items():
            if isinstance(param, GeneratorParamGroup):
                param_dict[name] = param.get_dict_values()
            else:
                param_dict[name] = param.value
        return param_dict

    def set_dict_values(self, param_values: dict[str, Any]):
        """
        Set the current values of parameters in this group.

        Accepts a nested dictionary containing desired parameter values.

        The input of this method accepts a shape compatible with the output
        of `get_dict_values`.

        If a provided parameter is not found, a :class:`ParamNotFoundException` is thrown.
        If a provided parameter is found, but its type differs from the provided parameter value,
        a :class:`WrongParamTypeException` is thrown.
        If a provided parameter value fails validation, a :class:`InvalidParamValueException` is thrown.

        :raises ParamNotFoundException: Parameter name not found
        :raises WrongParamTypeException: Parameter to set has wrong type
        :raises InvalidParamValueException: Parameter fails validation

        :param param_values: Nested dictionary containing parameter values
        """
        for name, param in param_values.items():
            if name not in self.params:
                raise ParamNotFoundException(f'Parameter "{name}" not found')

            current_param = self.params[name]
            if isinstance(param, dict):
                if not isinstance(current_param, GeneratorParamGroup):
                    expected_type = current_param.param_type
                    raise WrongParamTypeException(
                        f"Wrong param type for {name}. Expected {expected_type}, got dict"
                    )
                current_param.set_dict_values(param)
            else:
                if not isinstance(current_param, GeneratorParam):
                    raise WrongParamTypeException(
                        f"Wrong param type for {name}. Expected dict, got {type(param)}"
                    )
                current_param.value = param


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
        self._value: T = default_value
        self.default_value: T = default_value
        self.param_type: ParamType = param_type

    def reset(self):
        """Reset the parameter value to its default."""
        self._value = self.default_value

    @property
    def value(self):
        """Get the current value of this parameter."""
        return self._value

    @value.setter
    def value(self, value: Any):
        """
        Set the value of the parameter.

        Enforces typechecking and validation.
        Throws a :class:`WrongParamTypeException` if the provided value has an incorrect type.
        Throws a :class:`InvalidParamValueException` if the provided value fails validation.

        :raises WrongParamTypeException: Parameter value has incorrect type
        :raises InvalidParamValueException: Validation checks fail
        """
        if not type(value) == self.param_type.value:
            raise WrongParamTypeException(
                f"Wrong param type for {self.name}. Expected {self.param_type.value}, got {type(value)} ({value})"
            )
        self._validate_param_value(value)
        self._value = value

    @abstractmethod
    def _validate_param_value(self, value: T):
        """
        Validate a param value against custom semantics.

        Raises an :class:`InvalidParamValueException` when checks fail.

        :raises InvalidParamValueException: Validation checks fail

        :param value: The value to validate
        """
        pass


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

    def _validate_param_value(self, value: int):
        """
        Validate that a value is within the parameter's bounds.

        Raises a :class:`InvalidParamValueException` when checks fail.

        :raises InvalidParamValueException: Value is outside parameter's bounds

        :param value: The value to validate
        """
        if not (self.min_value <= value <= self.max_value):
            raise InvalidParamValueException(
                f"Param value must be within {self.min_value}-{self.max_value}. Got {value}."
            )


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
        default_value: float,
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

    def _validate_param_value(self, value: float):
        """
        Validate that a value is within the parameter's bounds.

        Raises a :class:`InvalidParamValueException` when checks fail.

        :raises InvalidParamValueException: Value is outside parameter's bounds

        :param value: The value to validate
        """
        if not (self.min_value <= value <= self.max_value):
            raise InvalidParamValueException(
                f"Param value must be within {self.min_value}-{self.max_value}. Got {value}."
            )


class EnumParam(GeneratorParam[str]):
    """
    A parameter taking an enum value.

    :ivar options: The options to choose from
    :vartype options: list[str]
    """

    def __init__(
        self, name: str, description: str, default_value: str, options: list[str]
    ):
        """
        Initialize an enum generator param.

        :param name: The name of this parameter
        :param description: A human-readable description of this parameter
        :param default_value: The default value of this parameter
        :param options: The options to choose from
        """
        super().__init__(name, description, ParamType.Enum, default_value)
        self.options: list[str] = options

    def _validate_param_value(self, value: str):
        """
        Validate that a value is within the parameter's bounds.

        Raises a :class:`InvalidParamValueException` when checks fail.

        :raises InvalidParamValueException: Value is outside parameter's bounds

        :param value: The value to validate
        """
        if value not in self.options:
            raise InvalidParamValueException(
                f"Param value must be one of {self.options}. Got {value}."
            )
