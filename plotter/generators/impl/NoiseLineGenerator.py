import math
import random
from enum import StrEnum
from typing import Any

from plotter.utils.splines import generate_line, sample_spline

from ...models import Model
from ...pens import Pen
from ..Generator import Generator
from ..Parameters import EnumParam, FloatParam, GeneratorParamGroup, IntParam


class UniqueLinePlacementStrategy(StrEnum):
    """The strategy to use for placing unique lines."""

    Uniform = "uniform"
    Random = "rand"


class NoiseLineGenerator(Generator):
    """
    NoiseLineGenerator is a generator that generates... lines... with some noise.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = "noisy lines"
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
                ),
                EnumParam(
                    "unique_line_placement_strategy",
                    "Strategy to use for placing unique lines vertically",
                    str(UniqueLinePlacementStrategy.Uniform),
                    [x.value for x in UniqueLinePlacementStrategy],
                ),
                IntParam(
                    "line_length", "Total length of line on y axis", 3000, 0, 20000
                ),
                IntParam(
                    "line_distance",
                    "Base distance between consecutive lines",
                    20,
                    0,
                    500,
                ),
                IntParam(
                    "line_distance_rand_amp",
                    "Amplitude of randomness added to distance between consecutive lines",
                    20,
                    0,
                    500,
                ),
                IntParam(
                    "line_distance_sin_amp",
                    "Amplitude of sin added to distance between consecutive lines",
                    5,
                    0,
                    500,
                ),
                IntParam(
                    "num_control_points",
                    "Number of control points to use for each line",
                    50,
                    0,
                    1000,
                ),
                IntParam(
                    "num_spline_samples", "Number of samples per spline", 500, 1, 5000
                ),
                IntParam(
                    "spline_tightness",
                    "Tightness parameter for spline generation",
                    0,
                    -1000,
                    1000,
                ),
                GeneratorParamGroup(
                    "x_axis",
                    [
                        IntParam(
                            "line_x_sin_amp",
                            "Amplitude of sinusoidal variation for x component of line generation",
                            100,
                            0,
                            1000,
                        ),
                        FloatParam(
                            "line_x_sin_amp_exp",
                            "Exponential factor for amplitude of sinusoidal variation for x component of line generation",
                            0.4,
                            0,
                            10,
                        ),
                        IntParam(
                            "line_x_sin_freq",
                            "Frequency of sinusoidal variation for x component of line generation",
                            50,
                            0,
                            1000,
                        ),
                        FloatParam(
                            "line_x_sin_freq_exp",
                            "Exponential factor for frequency of sinusoidal variation for x component of line generation",
                            0.4,
                            0,
                            10,
                        ),
                        IntParam(
                            "line_x_rand_amp",
                            "Amplitude of random variation for x component of line generation",
                            50,
                            0,
                            1000,
                        ),
                        FloatParam(
                            "line_x_rand_amp_exp",
                            "Exponential factor for amplitude of random variation for x component of line generation",
                            0.4,
                            0,
                            10,
                        ),
                    ],
                ),
                GeneratorParamGroup(
                    "y_axis",
                    [
                        IntParam(
                            "line_y_sin_amp",
                            "Amplitude of sinusoidal variation for y component of line generation",
                            100,
                            0,
                            1000,
                        ),
                        FloatParam(
                            "line_y_sin_amp_exp",
                            "Exponential factor for amplitude of sinusoidal variation for y component of line generation",
                            0.4,
                            0,
                            10,
                        ),
                        IntParam(
                            "line_y_sin_freq",
                            "Frequency of sinusoidal variation for y component of line generation",
                            50,
                            0,
                            1000,
                        ),
                        FloatParam(
                            "line_y_sin_freq_exp",
                            "Exponential factor for frequency of sinusoidal variation for y component of line generation",
                            0.4,
                            0,
                            10,
                        ),
                        IntParam(
                            "line_y_rand_amp",
                            "Amplitude of random variation for y component of line generation",
                            50,
                            0,
                            1000,
                        ),
                        FloatParam(
                            "line_y_rand_amp_exp",
                            "Exponential factor for amplitude of random variation for y component of line generation",
                            0.4,
                            0,
                            10,
                        ),
                    ],
                ),
            ],
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionary of the current parameter values
        :return: A model representing the generated scene
        """
        # Define margins
        y_offsets = []

        # First, pick y offsets of each line
        cum_translation_y = 0
        num_lines = param_dict["num_lines"]

        line_distance = param_dict["line_distance"]
        line_distance_rand_amp = param_dict["line_distance_rand_amp"]
        for i in range(num_lines):
            cum_translation_y += round(
                line_distance
                + random.randint(-line_distance_rand_amp, line_distance_rand_amp)
                + param_dict["line_distance_sin_amp"] * math.sin(i * (2 * math.pi) / 20)
            )
            y_offsets.append(cum_translation_y)

        # We want to lerp into a new random line every so often.
        # We have different strategies for choosing where to place these lines.
        num_unique_lines = param_dict["num_unique_lines"]
        unique_line_placement_strategy = param_dict["unique_line_placement_strategy"]
        unique_line_indices = []
        if unique_line_placement_strategy == UniqueLinePlacementStrategy.Uniform:
            lines_per_unique = num_lines / (num_unique_lines + 1)
            unique_line_indices = [
                round(i * lines_per_unique) for i in range(1, num_unique_lines + 1)
            ]
        elif unique_line_placement_strategy == UniqueLinePlacementStrategy.Random:
            unique_line_indices = sorted(
                random.sample(list(range(num_lines)), num_unique_lines)
            )
        else:
            raise Exception(
                f'Unknown line placement strategy "{unique_line_placement_strategy}"'
            )
        unique_line_indices = [0] + unique_line_indices + [num_lines - 1]

        # Generate unique lines
        points_per_line = param_dict["num_control_points"]
        x_var_dict = param_dict["x_axis"]
        y_var_dict = param_dict["y_axis"]
        unique_lines = [
            generate_line(
                0,
                param_dict["line_length"],
                0,
                points_per_line,
                x_sin_amp=x_var_dict["line_x_sin_amp"],
                x_sin_freq=x_var_dict["line_x_sin_freq"],
                x_rand_amp=x_var_dict["line_x_rand_amp"],
                x_sin_amp_exp=x_var_dict["line_x_sin_amp_exp"],
                x_sin_freq_exp=x_var_dict["line_x_sin_freq_exp"],
                x_rand_amp_exp=x_var_dict["line_x_rand_amp_exp"],
                y_sin_amp=y_var_dict["line_y_sin_amp"],
                y_sin_freq=y_var_dict["line_y_sin_freq"],
                y_rand_amp=y_var_dict["line_y_rand_amp"],
                y_sin_amp_exp=y_var_dict["line_y_sin_amp_exp"],
                y_sin_freq_exp=y_var_dict["line_y_sin_freq_exp"],
                y_rand_amp_exp=y_var_dict["line_y_rand_amp_exp"],
                pen=Pen.One,
            )
            for i in range(num_unique_lines + 2)  # Add two for start/end
        ]

        # Create a mapping of line indices to actual lines, and seed it with the unique lines
        line_map = {}
        for index, line in zip(unique_line_indices, unique_lines):
            line.translate(0, y_offsets[index])
            line_map[index] = line

        # For each line to draw, generate the actual line.
        current_unique_index = -1
        next_unique_index = -1
        for i in range(num_lines - 1):
            # If we've already have a line saved, that means it's one of the "unique" lines, so
            # set it as the current unique line and set the next one to look at
            if i in line_map:
                current_unique_index = i
                next_unique_index = unique_line_indices[
                    unique_line_indices.index(i) + 1
                ]
                continue
            # If we haven't seen this line before, we want to lerp between the current unique index and the next one.
            fraction_till_next_line = (
                y_offsets[i] - y_offsets[current_unique_index]
            ) / (
                y_offsets[next_unique_index] - y_offsets[current_unique_index]
            )  # This will be the ratio for lerping

            lerped_line = line_map[current_unique_index].lerp_points(
                line_map[next_unique_index], fraction_till_next_line
            )
            line_map[i] = lerped_line

        # Now, we have all of our lines. Turn them into splines!
        n_spline_samples = param_dict["num_spline_samples"]
        model = Model()
        for i in range(num_lines):
            line = sample_spline(
                line_map[i], n_spline_samples, param_dict["spline_tightness"]
            )
            model.add_line(line)

        return model
