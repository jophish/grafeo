from typing import Any

from ...models import Model
from ...models.atoms import Line, Point
from plotter.pens.Pen import Pen
from ..Generator import Generator
from ..Parameters import GeneratorParamGroup, IntParam, FloatParam
from plotter.models.derived.Box import Box
import random

class Disarray(Generator):
    """
    Test generator.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = "Disarray"
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
                FloatParam("object_size", "base size of object", 50.0, 1, 200),
                IntParam("rows", "num rows", 2, 1, 100),
                IntParam("cols", "num cols", 13, 1, 100),
                FloatParam("hatch_chance_top", "chance to hatch at first row", .03, 0, 1),
                FloatParam("hatch_chance_bottom", "chance to hatch at last row", .4, 0, 1),
                FloatParam("deg_random_scaling", "factor to multiply random degree by", .7, 0, 5),
                FloatParam("dims_random_scaling", "factor to multiply random dimensions by", .4, 0, 5),
                FloatParam("spacing_top_min", "min hatch spacing on first row", .6, .01, 100),
                FloatParam("spacing_top_max", "max hatch spacing on first row", .10, .01, 100),
                FloatParam("spacing_bottom_min", "min hatch spacing on last row", .1, .01, 100),
                FloatParam("spacing_bottom_max", "max hatch spacing on last row", .7, .01, 100),
                FloatParam("hatch_angle_random_scaling", "factor to multiply random angle by", .4, 0, 5)
            ],
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionar
y of the current parameter values
        :return: A model representing the generated scene
        """
        rows = param_dict["rows"]
        cols = param_dict["cols"]
        size = param_dict["object_size"]

        model = Model()
        for i in range(rows):
            for j in range(cols):
                deg = 0
                if i > 2:
                    deg = random.uniform(-i*param_dict["deg_random_scaling"], i*param_dict["deg_random_scaling"])

                random_x = random.uniform(-i*param_dict["dims_random_scaling"], i*param_dict["dims_random_scaling"])
                random_y = random.uniform(-i*param_dict["dims_random_scaling"], i*param_dict["dims_random_scaling"])

                box = Box(size + random_x, size + random_y, (size + random_x)/2, (size + random_y)/2)
                box.draw_outline(Pen.One)

                # Random chance to hatch. Hatching is less likely on higher rows, and the spacing will be larger, typically
                value = random.randint(0, 100)
                threshold = (param_dict["hatch_chance_top"] + i/rows*(param_dict["hatch_chance_bottom"] - param_dict["hatch_chance_top"])) * 100

                if value < threshold:
                    max_spacing = param_dict["spacing_top_max"] + (param_dict["spacing_bottom_max"] - param_dict["spacing_top_max"]) * i / rows
                    min_spacing = param_dict["spacing_top_min"] + (param_dict["spacing_bottom_min"] - param_dict["spacing_top_min"]) * i / rows
                    spacing = random.uniform(min_spacing, max_spacing)
                    pen = random.choice([Pen.One, Pen.Two, Pen.Three, Pen.Four])
                    random_spacing = random.uniform(-i, i)
                    box.hatch(pen, 45 + random_spacing*param_dict["hatch_angle_random_scaling"], spacing)

                box.rotate(deg, 0, 0)
                box.translate(j*size, i*-size)

                model.add_model(box)

        return model
