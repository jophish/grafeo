from typing import Any

from ...models import Model
from ..Generator import Generator
from ..Parameters import GeneratorParamGroup, EnumParam, FloatParam
from ...fonts.FontManager import FontManager
import os
from pathlib import Path

lorem_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/lorem.txt')


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
                    "content",
                    "content to use",
                    "char test",
                    ["char test", "lorem"],
                ),
                EnumParam(
                    "font",
                    "font to use",
                    fonts[0],
                    fonts,
                ),
                EnumParam(
                    "hatch",
                    "whether to hatch or not",
                    "true",
                    ["true", "false"],
                ),
                FloatParam("spacing", "hatching spacing", 2.0, 0, 200),
                FloatParam("angle", "hatching angle", 45.0, -90, 90),

            ],
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionary of the current parameter values
        :return: A model representing the generated scene
        """

        font_manager = FontManager()
        font_family = font_manager.get_font_family(param_dict['font'])
        text_model = Model()

        hatch_spacing = param_dict['spacing'] if param_dict['hatch'] == 'true'else None
        hatch_angle = param_dict['angle'] if param_dict['hatch'] == 'true' else None

        char_rows = []
        if param_dict['content'] == 'char test':
            chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
            per_row = 10
            char_rows = [chars[i:i+per_row] for i in range(0, len(chars), per_row)]
            text_model = font_family.get_text_model(char_rows, hatch_angle, hatch_spacing)
        else:
            lorem_text = Path(lorem_path).read_text()
            paragraphs = lorem_text.split('\n\n')

            per_row = 50
            para_char_rows = [[paragraph[i:i+per_row].strip('\n') for i in range(0, len(paragraph), per_row)] for paragraph in paragraphs]
            text_models = [font_family.get_text_model(char_row, hatch_angle, hatch_spacing) for char_row in para_char_rows]

            row_height = abs(font_family.ascent) + abs(font_family.descent)
            for i in range(len(text_models)):
                num_rows = sum([len(para_char_rows[j]) for j in range(i)]) + i
                text_models[i].translate(0, -num_rows * row_height)
                text_model.add_model(text_models[i])

        return text_model
