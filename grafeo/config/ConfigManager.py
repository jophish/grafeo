import json
import os
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from ..pens import Pen
import shutil
from ..utils.deep_merge import deep_merge_dicts
from ..generators import Generator, GeneratorParamGroup
import copy

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILENAME = "grafeo_config.json"
PENS_FILENAME = "grafeo_pens.json"
CONFIG_DIR = os.path.join(Path.home(), ".config/grafeo/")

CONFIG_PATH = os.path.join(
    CONFIG_DIR, CONFIG_FILENAME
)
PENS_PATH = os.path.join(
    CONFIG_DIR, PENS_FILENAME
)

PRINTERS_FILENAME = "printers.json"
PRINTERS_PATH = Path(CURRENT_PATH, PRINTERS_FILENAME)

DEFAULT_PENS_FILENAME = 'default_pens.json'
DEFAULT_PENS_PATH = Path(CURRENT_PATH, DEFAULT_PENS_FILENAME)

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
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self._init_pens()
        self._load_printers()
        self._init_config()

    def _load_printers(self):
        with open(PRINTERS_PATH) as f:
            self.printers = json.load(f)

    def _init_pens(self):
        if not Path.is_file(Path(PENS_PATH)):
            shutil.copyfile(DEFAULT_PENS_PATH, PENS_PATH)
        self._load_pens()

    def _load_pens(self):
        with open(PENS_PATH) as f:
            self.pens = json.load(f)

    def _init_config(self):
        if not Path.is_file(Path(CONFIG_PATH)):
            self.config = self._get_default_config()
            self.write_config_to_disk()
        else:
            self.load_config()

    def load_config(self):
        """
        Load config from disk into memory.

        Merges default configs with current configuration

        If a generator does not exist on disk during loading, the config on disk will be
        updated with the defaults from the missing generator.
        """
        existing_config = {}
        with open(CONFIG_PATH) as f:
            existing_config = json.load(f)

        default_config = self._get_default_config()

        self.config = deep_merge_dicts(default_config, existing_config)
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
        if not self.get_current_printer():
            return deep_merge_dicts(self.config['print_settings'], self.config['print_defaults'])
        else:
            printer_config = self.get_current_printer()
            return deep_merge_dicts(self.config['print_settings'], {
                "resolution_x": printer_config['resolution_x'],
                "resolution_y": printer_config['resolution_y'],
                "margin_x": printer_config['margin_x'],
                "margin_y": printer_config['margin_y'],
            })


    def get_title_settings(self) -> dict[str, Any]:
        """
        Return the current title settings.

        :return: Current title settings
        """
        return self.config["title_settings"]

    def get_serial_settings(self) -> dict[str, Any] | None:
        """
        Return the current serial settings.

        If no printer is currently selected that supports a serial connection,
        returns None.

        :return: Current serial settings, or None
        """
        if self.config['current_printer']:
            printer_config = self.get_current_printer()
            if printer_config['connection'] == 'serial':
                return printer_config['connection_defaults']

        return None

    def get_current_printer(self) -> dict[str, Any] | None:
        """
        Return the current printer config.

        :return: Current printer config, or None if no printer set.
        """
        if self.config['current_printer']:
            return list(filter(lambda x: x['name'] == self.config['current_printer'], self.config['printers']))[0]
        return None

    def set_current_printer(self, printer_name):
        self.config['current_printer'] = printer_name
        self.write_config_to_disk()

    def get_all_printers(self) -> dict[str, Any]:
        return {printer_config['name']: printer_config for printer_config in self.config['printers']}

    def update_current_printer_connection_setting(self, name: str, value: Any):
        current_printer = self.get_current_printer()
        if current_printer:
            current_printer['connection_defaults'][name] = value
            self.write_config_to_disk()

    def update_print_setting(self, name: str, value: Any):
        """
        Update an individual print setting.

        :param name: Name of parameter to update
        :param value: Value of parameter to update
        """

        if name == 'margin_x' or name == 'margin_y':
            current_printer = self.get_current_printer()
            if current_printer:
                current_printer[name] = value
            else:
                self.config['print_defaults'][name] = value
        else:
            self.config['print_settings'][name] = value
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
        for i in range(len(self.pens)):
            pen = self.pens[i]
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
            return {pen: self.pens[i] for pen, i in pen_map.items()}
        else:
            generator_pen_map = self.config['generator_pen_map'][generator_name]
            pen_map = {}
            dirty = False
            for pen in pens:
                if str(pen.value) not in generator_pen_map:
                    dirty = True
                    self.config['generator_pen_map'][generator_name][str(pen.value)] = default_pen_index

                if generator_pen_map[str(pen.value)] >= len(self.pens):
                    pen_map[str(pen.value)] = self.pens[default_pen_index]
                else:
                    pen_map[str(pen.value)] = self.pens[generator_pen_map[str(pen.value)]]
            if dirty:
                self.write_config_to_disk()
            return pen_map

    def get_pen_index_by_desc(self, descr: str) -> int:
        for i in range(len(self.pens)):
            if self.pens[i]['descr'] == descr:
                return i

    def get_available_pen_configs(self) -> list[dict[str, Any]]:
        """
        Return a list of available pen configs.

        :return: List of pen configs.
        """
        return self.pens

    def update_pen_map(self, generator_name: str, pen: Pen, index: int):
        """
        Update the mapping for a pen for a particular generator.

        :param generator_name:  Name of generator to update
        :param pen: Pen mapping to update (key)
        :param index: Index of pen config to map pen to (value)
        """
        self.config['generator_pen_map'][generator_name][pen] = index
        self.write_config_to_disk()

    def _get_default_printers(self):
        printer_configs = []
        for printer in self.printers:
            default_config = copy.deepcopy(printer)
            default_config["margin_x"] = default_config["default_margin_x"]
            default_config["margin_y"] = default_config["default_margin_y"]
            if default_config["connection"] == "serial":
                default_config["connection_defaults"]["port"] = None
            printer_configs.append(default_config)
        return printer_configs

    def _get_default_config(self):
        # Get default configs from each generator
        default_generator = list(self.generator_defaults.keys())[0]
        default_config = {
            # These defaults are required to render stuff to the screen
            # in the case where the user has not selected a printer.
            "print_defaults": {
                "margin_x": 500,
                "margin_y": 500,
                "resolution_x": 16640,
                "resolution_y": 10720
            },
            "generator_params": self._get_all_defaults(),
            "generator_pen_map": {},
            "current_printer": None,
            "printers": self._get_default_printers(),
            "current_generator": default_generator,
            "print_settings": {
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
                    "scale": 1,
                    "rotation": 0,
                    "translate_x": 0,
                    "translate_y": 0,
                    "pen": "Micron 005 Black",
                },
                "subtitle": {
                    "show": False,
                    "font": "Helvetica",
                    "value": "Subitle goes here",
                    "hatch": False,
                    "hatch_angle": 45,
                    "hatch_spacing": 10,
                    "scale": 1,
                    "rotation": 0,
                    "translate_x": 0,
                    "translate_y": -45,
                    "pen": "Micron 005 Black",
                }
            }
        }
        return default_config
