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
            new_lines.append([line[0] + x, line[1] + y, line[2] + z])
        self.lines = new_lines

    def rotate(self, x_angle, y_angle, z_angle):
        _, rot_mat = cv2.Rodrigues([[x_angle* math.pi / 180.0, y_angle * math.pi / 180.0, z_angle * math.pi / 180.0]])

    def perspective_projection(self, normal, point_on_plane):
        A, B, C = normal
        x0, y0, z0 = point_on_plane

        # Plane equation constant D
        D = -(A * x0 + B * y0 + C * z0)

        projected_model = Model()
        for line in self.lines:
            projected_points = []
            print('new line')
            for point in line:
                # Calculate signed distance from point to the plane
                d = (A * point[0] + B * point[1] + C * point[2] + D) / math.sqrt(A**2 + B**2 + C**2)

                # Project the point onto the plane
                x_proj = point[0] - d * (A / math.sqrt(A**2 + B**2 + C**2))
                y_proj = point[1] - d * (B / math.sqrt(A**2 + B**2 + C**2))

                projected_points.append(Point(x_proj, y_proj, Pen.One))
                print(d)
                print(x_proj, y_proj)
            projected_model.add_line(Line(projected_points, Pen.One))

        return projected_model

    def perspective_projection2(self, camera_matrix, dist_coeffs, rvec, tvec):

        projected_model = Model()
        for line in self.lines:
            points_2d, _ = cv2.projectPoints(
                np.array([line], np.float32),
                rvec, tvec,
                camera_matrix,
                dist_coeffs)

            line_points = []
            for point in points_2d:
                line_points.append(Point(point[0][0], point[0][1], Pen.One))
            projected_model.add_line(Line(line_points, Pen.One))

        return projected_model
