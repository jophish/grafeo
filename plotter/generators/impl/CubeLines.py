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

class CubeLines(Generator):
    """
    Test generator.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = "CubeLines"
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
                FloatParam("frustrum", "frustrum length", 1.0, 0, 100),
                FloatParam("rot_x", "object rotation about x axis", 0.0, -360, 360),
                FloatParam("rot_y", "object rotation about y axis", -45.0, -360, 360),
                FloatParam("rot_z", "object rotation about z axis", -45.0, -360, 360),
                FloatParam("trans_x", "object translate x", 0.0, -100, 100),
                FloatParam("trans_y", "object translate y", 0.0, -100, 100),
                FloatParam("trans_z", "object translate z", -10.0, -2000, 2000),
                IntParam("num_cubes", "num cubes", 50, 0, 10000),
                FloatParam("bound_x", "bound on x-axis for cube generation", 50.0, 0, 1000),
                FloatParam("bound_y", "bound on y-axis for cube generation", 50.0, 0, 1000),
                FloatParam("bound_z", "bound on z-axis for cube generation", 50.0, 0, 1000),
                FloatParam("min_side_len", "minimum side length", 1.0, 0, 1000),
                FloatParam("max_side_len", "maximum side length", 1.0, 0, 1000),
            ],
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionar
        y of the current parameter values
        :return: A model representing the generated scene
        """
        volumes = []

        for i in range(param_dict["num_cubes"]):
            volume = Volume()
            width = random.uniform(param_dict["min_side_len"], param_dict["max_side_len"])
            length = random.uniform(param_dict["min_side_len"], param_dict["max_side_len"])
            height = random.uniform(param_dict["min_side_len"], param_dict["max_side_len"])

            volume.add_line([[0,0,0], [0,0,0]])
            volume.add_line([[0,0,0], [length,0,0]])
            volume.add_line([[length,0,0], [length,width,0]])
            volume.add_line([[length,width,0], [0,width,0]])           #
            volume.add_line([[0,width,0], [0,0,0]])                     #

            volume.add_line([[0,0,height], [length,0,height]])           #
            volume.add_line([[length,0,height], [length,width,height]]) #
            volume.add_line([[length,width,height], [0,width,height]]) #
            volume.add_line([[0,width,height], [0,0,height]])           #

            volume.add_line([[0,0,0], [0,0,height]])                     #
            volume.add_line([[length,0,0], [length,0,height]])           #
            volume.add_line([[length,width,0], [length,width,height]]) #
            volume.add_line([[0, width,0], [0,width,height]])           #
            volume.translate(-length/2, -width/2, -height/2)


            rotate_x = random.uniform(-180, 180)
            rotate_y = random.uniform(-180, 180)
            rotate_z = random.uniform(-180, 180)
            # volume.rotate(rotate_x, rotate_y, rotate_z)

            offset_x = random.uniform(-param_dict["bound_x"], param_dict["bound_x"])
            offset_y = random.uniform(-param_dict["bound_y"], param_dict["bound_y"])
            offset_z = random.uniform(-param_dict["bound_z"], param_dict["bound_z"])
            volume.translate(offset_x, offset_y, offset_z)

            volumes.append(volume)

        model = Model()


        fx = param_dict["frustrum"]
        fy = param_dict["frustrum"]

        cx = 0
        cy = 0

        camera_matrix = np.array([[fx, 0, cx],
                          [0, fy, cy],
                          [0, 0, 1]], np.float32)
        dist_coeffs = np.zeros((5, 1), np.float32)

        x_rot = param_dict["rot_x"] * math.pi / 180.0
        y_rot = param_dict["rot_y"] * math.pi / 180.0
        z_rot = param_dict["rot_z"] * math.pi / 180.0
        rvec = np.array([[x_rot, y_rot, z_rot]], np.float32)
        # This tanslates the object into camera space
        tvec = np.array([[param_dict["trans_x"], param_dict["trans_y"], param_dict["trans_z"]]], np.float32)

        for volume in volumes:
            model.add_model(volume.perspective_projection(camera_matrix, dist_coeffs, rvec, tvec))

        return model
