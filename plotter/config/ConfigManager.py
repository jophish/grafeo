import json
import os
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from plotter.pens import Pen

from ..generators import Generator, GeneratorParamGroup

CONFIG_FILENAME = "pyplot.json"
CONFIG_PATH = os.path.join(
    Path(os.path.abspath(__file__)).parent.parent.parent.absolute(), CONFIG_FILENAME
)

@dataclass
class PenConfig:
    descr: str
    weight: int
    color: str
    location: int
    pause_to_replace: bool
    default: bool = False

@dataclass
class Config:
    generator_params: dict[str, Any]
    generator_pen_map: dict[str, dict[Pen, PenConfig]]
    current_generator: str
    print_settings: Any

class ConfigManager:
    """The ConfigManager class syncs configuration data between disk and memory."""

    def __init__(self, generator_defaults: dict[str, GeneratorParamGroup]):
        """Initialize a config manager."""
        self.generator_defaults: dict[str, GeneratorParamGroup] = generator_defaults
        self._init_config()

    def _init_config(self):
        if not Path.is_file(Path(CONFIG_PATH)):
            self._write_default_config()
        else:
            self.load_config()

    def load_config(self):
        """
        Load config from disk into memory.

        If a generator does not exist on disk during loading, the config on disk will be
        updated with the defaults from the missing generator.
        """
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)

        # If some generator is new and not yet in the config file, we should update the
        # config on disk with the new defaults.
        for generator_name in self.generator_defaults:
            if generator_name not in self.config["generator_params"]:
                self.config["generator_params"][
                    generator_name
                ] = self.generator_defaults[generator_name].get_dict_values()
        self.write_config_to_disk()

    def write_config_to_disk(self):
        """Write in-memory config to disk."""
        with open(CONFIG_PATH, "w") as f:
            f.write(json.dumps(self.config, indent=4))

    def get_current_generator(self):
        """Get the name of the current generator."""
        return self.config["current_generator"]

    def set_current_generator(self, generator_name):
        """Set the name of the current_generator."""
        self.config["current_generator"] = generator_name
        self.write_config_to_disk()

    def set_generator_params(self, generator: Generator):
        """
        Update the config for an entire generator.

        :param generator: The generator whose config to update.
        """
        self.config["generator_params"][
            generator.name
        ] = generator.params.get_dict_values()
        self.write_config_to_disk()

    def get_all_generator_param_values(self) -> dict[str, dict[str, Any]]:
        """
        Get all generator param values from the config.

        :return: A dictionary mapping generator names to param dictionaries.
        """
        return self.config["generator_params"]

    def _get_all_defaults(self) -> dict[str, dict[str, Any]]:
        return {
            name: generator_params.get_dict_values()
            for name, generator_params in self.generator_defaults.items()
        }

    def get_print_settings(self) -> dict[str, Any]:
        """
        Return the current print settings.

        :return: Current print settings
        """
        return self.config["print_settings"]

    def get_title_settings(self) -> dict[str, Any]:
        """
        Return the current title settings.

        :return: Current title settings
        """
        return self.config["title_settings"]

    def get_serial_settings(self) -> dict[str, Any]:
        """
        Return the current serial settings.

        :return: Current serial settings
        """
        return self.config["serial"]

    def update_print_setting(self, name: str, value: Any):
        """
        Update an individual print setting.

        :param name: Name of parameter to update
        :param value: Value of parameter to update
        """
        self.config["print_settings"][name] = value
        self.write_config_to_disk()

    def update_title_setting(self, title_type: str, name: str, value: Any):
        """
        Update an individual title setting.

        :param name: Name of parameter to update
        :param value: Value of parameter to update
        """
        self.config["title_settings"][title_type][name] = value
        self.write_config_to_disk()

    def _get_default_pen_index(self) -> int:
        for i in range(len(self.config['pens'])):
            pen = self.config['pens'][i]
            if 'default' in pen and pen['default']:
                return i

    def get_pen_map(self, generator_name: str, pens: set[Pen]) -> dict[Pen, PenConfig]:
        """
        Return a map from used pens to pen configs.

        If a used pen does not have a mapping set, will return a mapping
        to the default pen, and update the config with this new mapping.
        """
        default_pen_index = self._get_default_pen_index()
        if generator_name not in self.config['generator_pen_map']:
            pen_map = {pen: default_pen_index for pen in pens}
            self.config['generator_pen_map'][generator_name] = pen_map
            self.write_config_to_disk()
            return {pen: self.config['pens'][i] for pen, i in pen_map.items()}
        else:
            generator_pen_map = self.config['generator_pen_map'][generator_name]
            pen_map = {}
            dirty = False
            for pen in pens:
                if str(pen.value) not in generator_pen_map:
                    dirty = True
                    self.config['generator_pen_map'][generator_name][str(pen.value)] = default_pen_index
                pen_map[str(pen.value)] = self.config['pens'][generator_pen_map[str(pen.value)]]
            if dirty:
                self.write_config_to_disk()
            return pen_map

    def get_pen_index_by_desc(self, descr: str) -> int:
        for i in range(len(self.config['pens'])):
            if self.config['pens'][i]['descr'] == descr:
                return i

    def get_available_pen_configs(self) -> list[dict[str, Any]]:
        """
        Return a list of available pen configs.

        :return: List of pen configs.
        """
        return self.config['pens']

    def update_pen_map(self, generator_name: str, pen: Pen, index: int):
        """
        Update the mapping for a pen for a particular generator.

        :param generator_name:  Name of generator to update
        :param pen: Pen mapping to update (key)
        :param index: Index of pen config to map pen to (value)
        """
        self.config['generator_pen_map'][generator_name][pen] = index
        self.write_config_to_disk()

    def _write_default_config(self):
        # Get default configs from each generator
        default_generator = list(self.generator_defaults.keys())[0]
        default_config = {
            "generator_params": self._get_all_defaults(),
            "generator_pen_map": {},
            "serial": {
                "port": "/dev/ttyUSB0",
                "baud": 9600,
                "bytesize": 8,
                "parity": "even",
                "stopbits": 2,
                "flowcontrol": "xon/xoff",
            },
            "pens": [
                {
                    "descr": "Micron 005 Black",
                    "weight": 1,
                    "color": "#000000ff",
                    "location": 3,
                    "pause_to_replace": True,
                    "default": True,
                },
                {
                    "descr": "Prismacolor PM-31 (Dark Green)",
                    "weight": 5,
                    "color": "#40b43780",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-4 (Crimson Red)",
                    "weight": 5,
                    "color": "#e1020780",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-19 (Canary Yellow)",
                    "weight": 5,
                    "color": "#f7f70380",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-15 (Yellow Orange)",
                    "weight": 5,
                    "color": "#fca80380",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-61 (Dark Umber)",
                    "weight": 5,
                    "color": "#39171680",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-8 (Pink)",
                    "weight": 5,
                    "color": "#ff70ff80",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-50 (Violet)",
                    "weight": 5,
                    "color": "#260ffc80",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-44 (Ultramarine)",
                    "weight": 5,
                    "color": "#3370fa80",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-32 (Parrot Green)",
                    "weight": 5,
                    "color": "#3fd78180",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-98 (Black)",
                    "weight": 5,
                    "color": "#06080880",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-6 (Carmine Red)",
                    "weight": 5,
                    "color": "#ff578c80",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Prismacolor PM-53 (Mulberry)",
                    "weight": 5,
                    "color": "#c40dff80",
                    "location": 3,
                    "pause_to_replace": True,
                    "load_directly": True
                },
                {
                    "descr": "Micron 005 Red",
                    "weight": 1,
                    "color": "#eb4034ff",
                    "location": 3,
                    "pause_to_replace": True,
                }
            ],
            "current_generator": default_generator,
            "print_settings": {
                "margin_x": 500,
                "margin_y": 500,
                "max_x_coord": 16640,
                "max_y_coord": 10720,
                "scale": 1,
                "rotation": 0,
                "translate_x": 0,
                "translate_y": 0,
            },
            "title_settings": {
                "title": {
                    "show": False,
                    "font": "Helvetica",
                    "value": "Title goes here",
                    "hatch": False,
                    "hatch_angle": 45,
                    "hatch_spacing": 10,
                    "height": 30,
                    "rotation": 0,
                    "translate_x": 0,
                    "translate_y": 0,
                },
                "subtitle": {
                    "show": False,
                    "font": "Helvetica",
                    "value": "Subitle goes here",
                    "hatch": False,
                    "hatch_angle": 45,
                    "hatch_spacing": 10,
                    "height": 15,
                    "rotation": 0,
                    "translate_x": 0,
                    "translate_y": -45,
                }
            }
        }
        self.config = default_config
        self.write_config_to_disk()
