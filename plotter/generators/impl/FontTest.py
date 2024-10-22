from typing import Any

from ...models import Model
from ...models.atoms import Line, Point
from ...pens import Pen
from ..Generator import Generator
from ..Parameters import GeneratorParamGroup, IntParam, EnumParam
from plotter.fonts.FontManager import FontManager

class FontTest(Generator):
    """
    Test generator.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = "FontTest"
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
        font_manager = FontManager()
        fonts = font_manager.get_fonts()

        return GeneratorParamGroup(
            self.name,
            [
                EnumParam(
                    "font",
                    "font to use",
                    fonts[0],
                    fonts,
                ),
            ],
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionary of the current parameter values
        :return: A model representing the generated scene
        """
        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

        per_row = 10
        font_manager = FontManager()

        char_rows = [chars[i:i+per_row] for i in range(0, len(chars), per_row)]
        font_family = font_manager.get_font_family(param_dict['font'])

        text_model = font_family.get_text_model(char_rows)
        print(text_model.get_bounding_box())
        return text_model
