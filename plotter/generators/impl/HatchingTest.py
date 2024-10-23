from typing import Any

from ...models import Model
from ...models.atoms import Line, Point
from plotter.pens.Pen import Pen
from ..Generator import Generator
from ..Parameters import GeneratorParamGroup, IntParam, FloatParam
from plotter.models.derived.Box import Box

class HatchingTest(Generator):
    """
    Test generator.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = "HatcingTest"
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
                FloatParam("spacing", "hatching spacing", 2.0, 0, 20),
                FloatParam("angle", "hatching angle", 45.0, -90, 90),
            ],
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionary of the current parameter values
        :return: A model representing the generated scene
        """
        model = Model()
        box = Box(200, 400, 10, 10, Pen.One)
        box.hatch(Pen.One, param_dict["angle"], param_dict["spacing"])
        model.add_model(box)

        return model
