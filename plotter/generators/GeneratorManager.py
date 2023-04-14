from typing import Any

from plotter.generators.impl import generators

from ..models import Model
from .Generator import Generator
from .Parameters import GeneratorParamGroup


class GeneratorManager:
    """
    The GeneratorManager class is an interface for managing and organizing information about available generators.

    :ivar generators: A mapping from generator name to generator instances
    :vartype generators: dict[str, :class:`Generator`]
    :ivar current_generator: The currently selected generator
    :vartype current_generator: :class:`Generator`
    """

    def __init__(self):
        """Initialize a generator manager."""
        self._init_generators_with_defaults()

    def get_generator_defaults(self) -> dict[str, GeneratorParamGroup]:
        """
        Get default parameters for all generators.

        :return: A dictionary mapping generator name to its default parameter object
        """
        generator_defaults = {}
        for generator_name, generator in self.generators.items():
            generator_defaults[generator_name] = generator.get_default_params()
        return generator_defaults

    def _init_generators_with_defaults(self):
        """Initialize the class instance with default-valued generators."""
        self.generators: dict[str, Generator] = {}
        for generator in generators.values():
            init_generator = generator()
            self.generators[init_generator.name] = init_generator

    def get_generator_names(self):
        return [generator.name for generator in self.generators.values()]

    def set_current_generator(self, name):
        self.current_generator = self.generators[name]

    def set_all_generator_param_values(
        self, all_generator_param_values: dict[str, dict[str, Any]]
    ):
        for name, param_values in all_generator_param_values.items():
            self.generators[name].params.set_dict_values(param_values)

    def get_current_generator_param_value(self, param_name):
        return self.current_generator.get_param_values()[param_name]

    def generate_current(self) -> Model:
        return self.current_generator.generate()
