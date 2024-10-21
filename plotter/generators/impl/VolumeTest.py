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
                FloatParam("width", "width of object", 1.0, 0, 20),
                FloatParam("length", "length of object", 1.0, 0, 20),
                FloatParam("height", "height of object", 1.0, 0, 20),
                IntParam("slices", "slices in object", 10, 2, 200),
                IntParam("divs_per_slice", "divisions per slice", 10, 2, 200),
                FloatParam("frustrum", "frustrum length", 1.0, 0, 100),
                FloatParam("rot_x", "object rotation about x axis", 0.0, -360, 360),
                FloatParam("rot_y", "object rotation about y axis", -45.0, -360, 360),
                FloatParam("rot_z", "object rotation about z axis", -45.0, -360, 360),
                FloatParam("trans_x", "object translate x", 0.0, -100, 100),
                FloatParam("trans_y", "object translate y", 0.0, -100, 100),
                FloatParam("trans_z", "object translate z", -10.0, -100, 100),
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

        width = param_dict["width"]
        length = param_dict["length"]
        height = param_dict["height"]

        x_start = -width/2
        x_end = width/2
        for i in range(param_dict["slices"]):
            z = i/param_dict["slices"]*height - height/2
            for j in range(param_dict["divs_per_slice"]):
                y = j/param_dict["divs_per_slice"]*length - length/2
                volume.add_line([[x_start, y, z],[x_end, y, z]])


        ################################################################
        # volume.add_line([[0,0,0], [0,0,0]])                          #
        # volume.add_line([[0,0,0], [length,0,0]])                     #
        # volume.add_line([[length,0,0], [length,length,0]])           #
        # volume.add_line([[length,length,0], [0,length,0]])           #
        # volume.add_line([[0,length,0], [0,0,0]])                     #
        #                                                              #
        # volume.add_line([[0,0,length], [length,0,length]])           #
        # volume.add_line([[length,0,length], [length,length,length]]) #
        # volume.add_line([[length,length,length], [0,length,length]]) #
        # volume.add_line([[0,length,length], [0,0,length]])           #
        #                                                              #
        # volume.add_line([[0,0,0], [0,0,legth]])                     #
        # volume.add_line([[length,0,0], [length,0,length]])           #
        # volume.add_line([[length,length,0], [length,length,length]]) #
        # volume.add_line([[0,length,0], [0,length,length]])           #
        ################################################################

        # fustrum (distance from pinhole to image plane)
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

        # The camera is always at 0,0,0, pointing in the -z direction
        # rvec = np.zeros((3, 1), np.float32)

        # This tanslates the object into camera space
        tvec = np.array([[param_dict["trans_x"], param_dict["trans_y"], param_dict["trans_z"]]], np.float32)

        projected_model = volume.perspective_projection2(camera_matrix, dist_coeffs, rvec, tvec)

        return projected_model
