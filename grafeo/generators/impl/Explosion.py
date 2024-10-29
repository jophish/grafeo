from typing import Any

from ...models import Model
from ...models.atoms import Line, Point
from ...pens.Pen import Pen
from ..Generator import Generator
from ..Parameters import GeneratorParamGroup, IntParam, FloatParam, BoolParam
import numpy as np
import random

import pyln

class FullyStripedCube(pyln.Cube):
    def __init__(self, min_box, max_box, stripe_dist: int):
        # It is assumed that x and y length are multiples of stripe_dist
        super().__init__(min_box, max_box)
        self.stripe_dist = stripe_dist

    def paths(self) -> pyln.Paths:
        paths = []
        x1, y1, z1 = self.min[0], self.min[1], self.min[2]
        x2, y2, z2 = self.max[0], self.max[1], self.max[2]

        x_len = (x2 - x1)
        num_stripes_x_axis = round(x_len/self.stripe_dist + 1)

        # We don't want to draw the edge outline on the X-Y face that is occluded
        # by the visible X-Y face. How do we do this?
        # Idea:
        for i in range(num_stripes_x_axis):
            x = x1 + self.stripe_dist * i
            y_start = y1
            y_end = y2
            z_start = z1
            z_end = z2
            paths.append([[x, y_start, z_start], [x, y_start, z_end]])
            paths.append([[x, y_end, z_start], [x, y_end, z_end]])

            paths.append([[x, y_start, z_start], [x, y_end, z_start]])
            #paths.append([[x, y_start, z_end], [x, y_end, z_end]])

        y_len = (y2 - y1)
        num_stripes_y_axis = round(y_len/self.stripe_dist + 1)
        # Since we don't want to duplicate edges
        for i in range(1, num_stripes_y_axis - 1):
            y = y1 + self.stripe_dist*i

            x_start = x1
            x_end = x2
            z_start = z1
            z_end = z2
            paths.append([[x_start, y, z_start], [x_start, y, z_end]])
            paths.append([[x_end, y, z_start], [x_end, y, z_end]])
        return pyln.Paths(paths)

class StripedTriangle(pyln.Triangle):
    def __init__(self, min_box, max_box, stripe_dist: int):
        # It is assumed that x and y length are multiples of stripe_dist
        super().__init__(min_box, max_box)
        self.stripe_dist = stripe_dist

    def paths(self) -> pyln.Paths:
        paths = []
        x1, y1, z1 = self.min[0], self.min[1], self.min[2]
        x2, y2, z2 = self.max[0], self.max[1], self.max[2]

        x_len = (x2 - x1)
        num_stripes_x_axis = round(x_len/self.stripe_dist + 1)

        # We don't want to draw the edge outline on the X-Y face that is occluded
        # by the visible X-Y face. How do we do this?
        # Idea:
        for i in range(num_stripes_x_axis):
            x = x1 + self.stripe_dist * i
            y_start = y1
            y_end = y2
            z_start = z1
            z_end = z2
            paths.append([[x, y_start, z_start], [x, y_start, z_end]])
            paths.append([[x, y_end, z_start], [x, y_end, z_end]])

            paths.append([[x, y_start, z_start], [x, y_end, z_start]])
            #paths.append([[x, y_start, z_end], [x, y_end, z_end]])

        y_len = (y2 - y1)
        num_stripes_y_axis = round(y_len/self.stripe_dist + 1)
        # Since we don't want to duplicate edges
        for i in range(1, num_stripes_y_axis - 1):
            y = y1 + self.stripe_dist*i

            x_start = x1
            x_end = x2
            z_start = z1
            z_end = z2
            paths.append([[x_start, y, z_start], [x_start, y, z_end]])
            paths.append([[x_end, y, z_start], [x_end, y, z_end]])
        return pyln.Paths(paths)
class Explosion(Generator):
    """
    Test generator.

    :ivar name: The friendly name for this generator
    :vartype name: str
    """

    def __init__(self):
        """Initialize the generator."""
        self.name = "Explosion"
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
                FloatParam("aspect_ratio", "x/y aspect ratio", 16.0/9.0, 1, 10),
                IntParam("num_objects", "num objects", 100, 1, 500),
                FloatParam("stripe_dist", "distance between stripes", .5, .01, 10),
                IntParam("min_width", "min width, in # of stripes", 10, 3, 200),
                IntParam("max_width", "max width, in # of stripes", 60, 3, 200),
                IntParam("min_length", "min length, in # of stripes", 10, 3, 200),
                IntParam("max_length", "max length, in # of stripes", 60, 3, 200),
                FloatParam("min_height", "min height", .5, .01, 200),
                FloatParam("max_height", "min height", 3.0, .01, 200),
                BoolParam("occlude", "whether or not objects should occlude", False),
                FloatParam("step_size", "step size to sample for occlusion", 1.0, .001, 3),
            ],
        )

    def _generate(self, param_dict: dict[str, Any]) -> Model:
        """
        Generate a model using the current parameter values.

        :param param_dict: A nested dictionary of the current parameter values
        :return: A model representing the generated scene
        """
        pyln.utility.compile_numba()

        num_polys = param_dict['num_objects']

        stripe_dist = .5

        max_width = param_dict['max_width']
        min_width = param_dict['min_width']

        max_length = param_dict['max_length']
        min_length = param_dict['min_length']

        max_height = param_dict['max_height']
        min_height = param_dict['min_height']

        aspect_ratio = param_dict['aspect_ratio']
        max_std_dev = 100
        trans_std_dev_x = max_std_dev if aspect_ratio >= 1 else max_std_dev/aspect_ratio
        trans_std_dev_y = 50  # This just moves objects closer to/further from the camera
        trans_std_dev_z = max_std_dev if aspect_ratio < 1 else max_std_dev/aspect_ratio



        # define camera parameters
        eye = [0, -400.0, 0]  # camera position
        center = [0.0, 0.0, 0.0]  # camera looks at
        up = [0.0, 0.0, 1.0]  # up direction

        # define rendering parameters
        width = 1024  # rendered width
        height = 1024  # rendered height
        fovy = 100.0  # vertical field of view, degrees
        znear = 0.001  # near z plane
        zfar = 800.0  # far z plane
        step = param_dict['step_size']  # how finely to chop the paths for visibility testing

        polys = []
        while len(polys) < num_polys:
            trans_x = np.random.normal(0, trans_std_dev_x)
            trans_y = np.random.normal(0, trans_std_dev_y)
            trans_z = np.random.normal(0, trans_std_dev_z)

            # If the placement of an object is too extreme, skip it
            if (abs(trans_x) > trans_std_dev_x*2.5 or abs(trans_z) > trans_std_dev_z*2.5):
                continue

            fx = random.randint(min_width, max_width)*stripe_dist
            fy = random.randint(min_length, max_length)*stripe_dist
            fz = random.uniform(min_height, max_height)

            shape = FullyStripedCube([-fx/2, -fy/2, -fz/2], [fx/2, fy/2, fz/2], stripe_dist)

            # now rotate random amount. these rotations guarantee
            # we never see the bottom face.
            theta_x = random.uniform(-45, 45) + 90
            theta_y = random.uniform(-45, 45)
            theta_z = random.uniform(-45, 45)
            shape = shape.rotate_x(theta_x)
            shape = shape.rotate_y(theta_y)
            shape = shape.rotate_z(theta_z)


            shape = shape.translate(np.array([trans_x, trans_y, trans_z]))
            polys.append(shape)


        model = Model()
        if param_dict['occlude']:
            scene = pyln.Scene()
            for shape in polys:
                scene.add(shape)
            paths = scene.render(eye, center, up, width, height, fovy, znear, zfar, step)
            for path in paths.paths:
                model.add_line(Line(
                    [Point(point[0], point[1], Pen.One) for point in path.path],
                    Pen.One
                ))
        else:
            for shape in polys:
                scene = pyln.Scene()
                scene.add(shape)
                paths = scene.render(eye, center, up, width, height, fovy, znear, zfar, step)
                for path in paths.paths:
                    model.add_line(Line(
                        [Point(point[0], point[1], Pen.One) for point in path.path],
                        Pen.One
                    ))

        return model
