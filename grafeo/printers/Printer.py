from abc import ABC, abstractmethod
from typing import Any
from ..pens import Pen
from ..serializers.Serializer import Serializer
from ..config.ConfigManager import PenConfig
from ..models import Model
from ..utils.scaling import scale_to_fit
import math


class Printer(ABC):
    def __init__(self, serializer: Serializer):
        self.serializer = serializer
        self.command_buffer = []
        self.pen_maps = []
        self.printing = False
        self.printing_needs_user_input = False
        self.current_buffer_index = 0

    def has_serializer(self):
        return self.serializer != None

    def begin_print(self):
        if not self.serializer:
            return
        self.printing = True
        self.current_buffer_index = 0
        self.continue_print()

    @abstractmethod
    def pre_print_commands(self):
        pass

    @abstractmethod
    def generate_commands(self, lines, print_settings, pen_map):
        pass

    @abstractmethod
    def _continue_print(self):
        """
        Continue the print where it previously left off.

        Should return true if the print is finished, otherwise false.
        """
        pass

    def continue_print(self):
        if not self.printing:
            return

        self.printing_needs_user_input = False
        result = self._continue_print()
        if result:
            self.pen_maps = []
            self.command_buffer = []
            self.current_buffer_index = 0
            self.printing = False

    def add_to_print(
        self,
        model: Model,
        pen_map: dict[Pen, PenConfig],
        print_settings,
        translate_x,
        translate_y,
        scale,
        rotation
    ):
        """
        Given a model and some transformation parameters, generate commands and add to buffer.
        """
        self.pen_maps.append(pen_map)

        # TODO: A copy is expensive -- can we do better?
        model = model.copy()
        bounding_box = model.get_bounding_box()

        # Apply transforms here:
        # - Translate to be centered about origin
        bounding_box = model.get_bounding_box()
        bounding_box_center_x = (bounding_box.max_x + bounding_box.min_x)/2
        bounding_box_center_y = (bounding_box.max_y + bounding_box.min_y)/2
        model.translate(-bounding_box_center_x, -bounding_box_center_y)

        # - Scale to fit maximally within margins, then scale again by user-determined scale factor
        bounding_box = model.get_bounding_box()
        (scaled_x, scaled_y) = scale_to_fit(
            bounding_box.max_x - bounding_box.min_x,
            bounding_box.max_y - bounding_box.min_y,
            print_settings["resolution_x"] - print_settings["margin_x"]*2,
            print_settings["resolution_y"] - print_settings["margin_y"]*2
        )

        init_scale = scaled_x/(bounding_box.max_x - bounding_box.min_x)
        print_scale = scale
        final_scale = init_scale*print_scale

        model.apply_matrix([
            [final_scale, 0],
            [0, final_scale]
        ])
        bounding_box = model.get_bounding_box()

        # - Rotate about origin (since we're currently centered about origin)
        theta =  math.pi * rotation / 180.0
        rotation_matrix = [
            [math.cos(theta), -math.sin(theta)],
            [math.sin(theta), math.cos(theta)]
        ]
        model.apply_matrix(rotation_matrix)

        bounding_box = model.get_bounding_box()

        # - Finally, translate back into place in +x/+y quadrant, taking into account additional translations
        # If we don't flip the y translation, the printed image is shifted in the wrong direction...
        model.translate(print_settings["resolution_x"]/2 + translate_x, print_settings["resolution_y"]/2 - translate_y)
        bounding_box = model.get_bounding_box()

        model_lines = model.all_lines

        commands = self.generate_commands(model_lines, print_settings, pen_map)
        self.command_buffer.append(commands)
