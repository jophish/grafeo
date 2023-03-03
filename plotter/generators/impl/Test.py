from ..Generator import Generator
from ..Parameters import GeneratorParamGroup, IntParam
from ...models import Model
from ...models.atoms import Line, Point
from ...pens import Pen
from typing import Any


class Test(Generator):
    """
    Test generator.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = 'test'
        super().__init__(self.name)

    def get_default_params(self) -> GeneratorParamGroup:
        """
        Get parameters for this generator, set to their defaults.

        There are three main types of parameters for this generator:
        * "Global" parameters, e.g., controlling lines, splines, etc
        * Parameters controlling x-axis variation
        * Parameters controlling y-axis variation

        :return: The generator's parameters, initialized to their defaults
        """
        return GeneratorParamGroup(
            self.name,
            [
                IntParam("num_lines", "Number of lines to draw", 200, 5, 1000),
                IntParam(
                    "num_unique_lines",
                    "Number of unique lines to lerp between",
                    10,
                    0,
                    200,
                )
            ]
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionary of the current parameter values
        :return: A model representing the generated scene
        """
        model = Model()
        model.add_line(Line([
            Point(0, 0, Pen.One),
            Point(0, 0, Pen.One)
        ], Pen.One))
        return model
