from .Printer import Printer
from time import sleep
from collections import defaultdict
from ..models.atoms.Line import Line

def fmt(string):
    return string.encode() + b"\x03"

class GpglPrinter(Printer):
    def __init__(self, serializer):
        super().__init__(serializer)
        self.current_pen = None
        self.pen_to_replace = None

    def pre_print_commands(self):
        self.serializer.serialize_command(fmt(':'))
        sleep(5)
        self.serializer.serialize_command(fmt('M0, 0'))

    # Given a list of lines, returns a map from pen_num to a list of lines
    # using that pen.
    def _group_lines_by_pen(self, lines: list[Line]):
        pen_num_map = defaultdict(list)
        for line in lines:
            line_pen_num = line.pen
            pen_num_map[str(line_pen_num)].append(line)
        return pen_num_map

    def _continue_print(self):
        # This method is only called whenever a pen is replaced
        self.current_pen = self.pen_to_replace
        self.pen_to_replace = None

        # Iterate over buffers, popping items out until we see a "pen replace" command.
        # Once we see one, set some flags, and stop printing. The GUI will watch these flags
        # and prompt the user to replace the pen. Once it's been replaced, confirming the
        # dialogue will resume the print.
        while self.current_buffer_index < len(self.command_buffer):
            while len(self.command_buffer[self.current_buffer_index]) > 0:
                gpgl_command = self.command_buffer[self.current_buffer_index].pop(0)
                if gpgl_command[:2] == "PR":
                    new_pen_num = gpgl_command[2]
                    new_pen_config = self.pen_maps[self.current_buffer_index][new_pen_num]
                    self.serializer.serialize_command(fmt("J0")) # This returns the previous pen to the bay it was taken from
                    if self.current_pen and self.current_pen.get('load_directly', False):
                        # If the current pen was a "custom" pen that cannot fit into a bay,
                        # this additional J0 command allows the plotter to operate "without holding a pen"
                        # meaning it won't try to grab something from a bay when the next draw command
                        # is issued
                        self.serializer.serialize_command(fmt("J0"))

                    self.pen_to_replace = new_pen_config
                    self.printing_needs_user_input = True
                    return False
                self.serializer.serialize_command(fmt(gpgl_command))
            self.current_buffer_index += 1

        return True

    def generate_commands(self, lines, print_settings, pen_map):
        lines_grouped_by_pen = self._group_lines_by_pen(lines)

        gpgl = ["H"]
        current_pen = None

        for line_group in lines_grouped_by_pen.values():
            for line in line_group:
                line_pen_num = line.pen
                line_pen_config = pen_map[str(line_pen_num)]

                # If the current pen does not equal the desired pen for this line, get the desired pen.
                # If pause_to_replace is set, we should wait before getting the current pen.
                if (not current_pen) or pen_map[str(current_pen)]["descr"] != line_pen_config["descr"]:
                    if line_pen_config['pause_to_replace']:
                        gpgl.append(f"PR{line_pen_num}")
                        new_pen_location = line_pen_config['location']
                        if line_pen_config.get('load_directly', False):
                            gpgl.append('H')
                        else:
                            gpgl.append(f"J{new_pen_location}")
                        current_pen = line_pen_num

                # Now, the correct pen is in the holder, we can proceed.
                points = line.points
                for i in range(len(points)):
                    if i == 0:
                        # Using the y-component as-is results in a mirrored image about the horizontal axis;
                        # flip it here...
                        gpgl.append(
                            f'M{round(points[i].x)},{round(points[i].y)}'
                        )
                    else:
                        gpgl.append(
                            f'D{round(points[i].x)},{round(points[i].y)}'
                        )

        gpgl.append("J0")
        gpgl.append("H")

        return gpgl
