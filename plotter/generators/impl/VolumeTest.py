from typing import Any

from ...models import Model
from ...models.atoms import Line, Point
from plotter.pens.Pen import Pen
from ..Generator import Generator
from ..Parameters import GeneratorParamGroup, IntParam, FloatParam
from plotter.models.derived.Box import Box
import random
from plotter.volumes.Volume import Volume
import math
import numpy as np
import cv2

class VolumeTest(Generator):
    """
    Test generator.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = "VolumeTest"
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
        volume = Volume()
        width = 10
        height = 10
        for i in range(height):
            for j in range(width):
                pass
                # volume.add_line([[-width/2, -width/2 + j*2 , 5 + i*5], [width/2, -width/2 + j*2, 5 + i*5]])

        volume.add_line([[0,0,0], [0,0,0]])
        volume.add_line([[0,0,0], [1,0,0]])
        volume.add_line([[1,0,0], [1,1,0]])
        volume.add_line([[1,1,0], [0,1,0]])
        volume.add_line([[0,1,0], [0,0,0]])

        volume.add_line([[0,0,1], [1,0,1]])
        volume.add_line([[1,0,1], [1,1,1]])
        volume.add_line([[1,1,1], [0,1,1]])
        volume.add_line([[0,1,1], [0,0,1]])

        volume.add_line([[0,0,0], [0,0,1]])
        volume.add_line([[1,0,0], [1,0,1]])
        volume.add_line([[1,1,0], [1,1,1]])
        volume.add_line([[0,1,0], [0,1,1]])

        # fustrum (distance from pinhole to image plane)
        fx = 1
        fy = 1

        cx = -50
        cy = 1000

        camera_matrix = np.array([[fx, 0, cx],
                          [0, fy, cy],
                          [0, 0, 1]], np.float32)
        dist_coeffs = np.zeros((5, 1), np.float32)

        x_rot = 0
        y_rot = -45 * math.pi / 180.0
        z_rot = -45 * math.pi / 180.0
        rvec = np.array([[x_rot, y_rot, z_rot]], np.float32)

        # The camera is always at 0,0,0, pointing in the -z direction
        # rvec = np.zeros((3, 1), np.float32)

        tvec = np.array([[-.5, -.5, -10.5]], np.float32)

        projected_model = volume.perspective_projection2(camera_matrix, dist_coeffs, rvec, tvec)

        print(projected_model.get_bounding_box())
        return projected_model
