from abc import ABC, abstractmethod
from typing import Any

from ..models.Model import Model
from .Parameters import GeneratorParamGroup


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
    :vartype params: :class:`GeneratorParamGroup`
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
        self.model = Model()
        self.model = self._generate(self.params.get_dict_values())
        # For some unknown reason, this breaks shit if the model
        # was not already fully within the +x/+y quadrant
        # self.model.normalize()
        return self.model

    def reset_params(self):
        """Reset parameter values to defaults."""
        if not hasattr(self, "params"):
            self.params: GeneratorParamGroup = self.get_default_params()
        else:
            self.params.reset()

    @abstractmethod
    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a scene using provided parameters.

        :param param_dict: A nested dictionary of the current parameter values
        :return: A model representing the generated scene
        """
        pass

    @abstractmethod
    def get_default_params(self) -> GeneratorParamGroup:
        """
        Get the parameters for this generator, initialized to their default values.

        :return: An object describing the generator's parameters
        """
        pass
