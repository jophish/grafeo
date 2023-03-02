from abc import ABC, abstractmethod
from typing import Any, Dict

from ..models.Model import Model
from .Parameters import GeneratorParam


class Generator(ABC):
    """
    The Generator class provides an interface and framework for the generation of parameterized artwork.

    A child subclassing the Generator class must implement the following two methods:
    * `get_default_params`
    * `_generate`

    `get_default_params` describes all the parameters available to this model, initialized to their default values.
    `_generate` is responsible for actually generating artwork. When artwork is generated, `_generate` will be called
    with the current values of the generator's parameters. `_generate` is expected to return a :class:`Model` object,
    which represents a scene to be rendered.

    :ivar name: The friendly name for this generator
    :vartype name: str
    :ivar model: The most-recently generated model produced by this generator
    :vartype model: :class:`Model`
    :ivar params: The parameters used for this model
    :vartype params: :class:`Dict[str, :class:`GeneratorParam`]`
    """

    def __init__(self, name: str):
        """
        Initialize a generator.

        :param name: The friendly name for this generator
        """
        self.name: str = name
        self.model = Model()
        self.reset_params()

    def generate(self):
        """
        Generate using the current parameter values.

        This will update the `model` attribute of the generator.
        """
        self.model = self._generate(**self.params)

    def reset_params(self):
        """Reset parameter values to defaults."""
        self.params: Dict[str, GeneratorParam] = self.get_default_params()

    def set_param_value(self, name: str, value: Any):
        """
        Set the parameter with the given name to the given value.

        :param name: The name of the parameter to update
        :param value: The value to update the parameter to
        """
        self.params[name].value = value

    def set_param_values(self, values: Dict[str, Any]):
        """
        Update the value of multiple parameters at once.

        :param values: Dictionary mapping parameter names to new values
        """
        for name, value in values.items():
            self.params[name].value = value

    @abstractmethod
    def _generate(self, **kwargs) -> Model:
        """
        Generate a scene using provided parameters.

        :return: A model representing the generated scene
        """
        pass

    @abstractmethod
    def get_default_params(self) -> Dict[str, GeneratorParam]:
        """
        Get the parameters for this generator, initialized to their default values.

        :return: A dictionary mapping parameter names to their associated parameter objects
        """
        pass
