from collections import defaultdict

from ..models.atoms.Line import Line
from ..config.ConfigManager import PenConfig
from ..pens import Pen

# Class to generate GPGL based on a pen configuration and lines.
# This actually extends GPGL slightly. We add a new "command", "PRn" (pen replace),
# which tells our software to:
# 1. Return the pen to the pen bay
# 2. Prompt the user to load pen num n into the appropriate bay
# 2. Pause until user input
# 3. Continue sending GPGL commands as normal
# This allows the user to replace pens in a holder, if limited holders are available.
class GpglGenerator:
    def __init__(self, print_settings, pen_map: dict[Pen, PenConfig]):
        self.print_settings = print_settings
        self.pen_map = pen_map

    def set_pen_map(self, pen_map):
        self.pen_map = pen_map

    def set_lines(self, lines: list[Line]):
        self.lines = lines

    # Given a list of lines, returns a map from pen_num to a list of lines
    # using that pen.
    def group_lines_by_pen(self, lines: list[Line]):
        pen_num_map = defaultdict(list)
        for line in lines:
            line_pen_num = line.pen
            pen_num_map[str(line_pen_num)].append(line)
        return pen_num_map

    def generate_gpgl(self):
        if not self.lines:
            return None

        lines_grouped_by_pen = self.group_lines_by_pen(self.lines)

        gpgl = ["H"]
        current_pen = None

        for line_group in lines_grouped_by_pen.values():
            for line in line_group:
                line_pen_num = line.pen
                line_pen_config = self.pen_map[str(line_pen_num)]

                # If the current pen does not equal the desired pen for this line, get the desired pen.
                # If pause_to_replace is set, we should wait before getting the current pen.
                if (not current_pen) or self.pen_map[str(current_pen)]["descr"] != line_pen_config["descr"]:
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

        self.gpgl = gpgl
        return self.gpgl
