from ..models import Model
from ..gpgl.GpglGenerator import GpglGenerator
from ..config.ConfigManager import PenConfig
from ..pens import Pen
import serial
from time import sleep
from serial import EIGHTBITS, PARITY_EVEN, STOPBITS_TWO
import math
from ..utils.scaling import scale_to_fit

def fmt(string):
    return string.encode() + b"\x03"

class SerialPrinter():

    def __init__(self, serial_settings):
        self.serial_settings = serial_settings
        # self.ser = serial.Serial(             #
        #     port=serial_settings['port'],     #
        #     baudrate=serial_settings['baud'], #
        #     bytesize=EIGHTBITS,               #
        #     parity=PARITY_EVEN,               #
        #     stopbits=STOPBITS_TWO,            #
        #     timeout=1,                        #
        #     xonxoff=True,                     #
        # )                                     #
        self.gpgl_buffer = []
        self.pen_maps = []
        self.printing = False
        self.printing_needs_user_input = False
        self.current_pen = None
        self.pen_to_replace = None
        self.current_buffer_index = 0

    def continue_print(self):
        if not self.printing:
            return

        self.printing_needs_user_input = False

        # This method is only called whenever a pen is replaced
        self.current_pen = self.pen_to_replace
        self.pen_to_replace = None

        # Iterate over buffers, popping items out until we see a "pen replace" command.
        # Once we see one, set some flags, and stop printing. The GUI will watch these flags
        # and prompt the user to replace the pen. Once it's been replaced, confirming the
        # dialogue will resume the print.
        while self.current_buffer_index < len(self.gpgl_buffer):
            while len(self.gpgl_buffer[self.current_buffer_index]) > 0:
                gpgl_command = self.gpgl_buffer[self.current_buffer_index].pop(0)
                if gpgl_command[:2] == "PR":
                    new_pen_num = gpgl_command[2]
                    new_pen_config = self.pen_maps[self.current_buffer_index][new_pen_num]
                    self.ser.write(fmt("J0")) # This returns the previous pen to the bay it was taken from
                    if self.current_pen and self.current_pen.get('load_directly', False):
                        # If the current pen was a "custom" pen that cannot fit into a bay,
                        # this additional J0 command allows the plotter to operate "without holding a pen"
                        # meaning it won't try to grab something from a bay when the next draw command
                        # is issued
                        self.ser.write(fmt("J0"))

                    self.pen_to_replace = new_pen_config
                    self.printing_needs_user_input = True
                    return
                self.ser.write(fmt(gpgl_command))
            self.current_buffer_index += 1

        self.pen_maps = []
        self.gpgl_buffer = []
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
        Given a model and some transformation parameters, generate GPGL and add to print buffer.
        """
        self.pen_maps.append(pen_map)

        # TODO: A copy is expensive -- can we do better?
        model = model.copy()
        gpgl_generator = GpglGenerator(print_settings, pen_map)
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
            print_settings["max_x_coord"] - print_settings["margin_x"]*2,
            print_settings["max_y_coord"] - print_settings["margin_y"]*2
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
        model.translate(print_settings["max_x_coord"]/2 + translate_x, print_settings["max_y_coord"]/2 - translate_y)
        bounding_box = model.get_bounding_box()

        model_lines = model.all_lines

        gpgl_generator.set_lines(model_lines)
        gpgl = gpgl_generator.generate_gpgl()
        self.gpgl_buffer.append(gpgl)

    def begin_print(self):
        self.ser.write(fmt(":"))
        sleep(5)
        self.ser.write(fmt("M0, 0"))

        self.printing = True
        self.continue_print()
