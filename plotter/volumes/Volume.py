from plotter.models.atoms.Line import Line
from plotter.models.atoms.Point import Point
from plotter.models.Model import Model
from plotter.pens.Pen import Pen


import numpy as np
import cv2

import math

class Volume():

    def __init__(self):
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def translate(self, x, y, z):
        new_lines = []
        for line in self.lines:
            new_line = [[point[0] + x, point[1] + y, point[2] + z] for point in line]
            new_lines.append(new_line)
        self.lines = new_lines

    def rotate(self, x_angle, y_angle, z_angle):
        """
        Rotate volume about the origin.
        """

        rot_mat, _ = cv2.Rodrigues(np.array([[x_angle* math.pi / 180.0, y_angle * math.pi / 180.0, z_angle * math.pi / 180.0]], np.float32))

        new_lines = []
        for line in self.lines:
            new_line = [cv2.warpPerspective(np.array([[point[0], point[1], point[2]]]), rot_mat, (3,1)) for point in line]
            new_lines.append([[point[0][0], point[0][1], point[0][2]] for point in new_line])
        self.lines = new_lines

    def perspective_projection(self, camera_matrix, dist_coeffs, rvec, tvec):

        projected_model = Model()
        for line in self.lines:
            points_2d, _ = cv2.projectPoints(
                np.array([line], np.float32),
                rvec, tvec,
                camera_matrix,
                dist_coeffs)

            line_points = []
            for point in points_2d:
                line_points.append(Point(float(point[0][0]), float(point[0][1]), Pen.One))
            projected_model.add_line(Line(line_points, Pen.One))

        return projected_model
