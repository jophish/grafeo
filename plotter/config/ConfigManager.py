import json
import os
from pathlib import Path
from typing import Any

from ..generators import Generator, GeneratorParamGroup

CONFIG_FILENAME = "pyplot.json"
CONFIG_PATH = os.path.join(
    Path(os.path.abspath(__file__)).parent.parent.parent.absolute(), CONFIG_FILENAME
)


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

    def update_print_setting(self, name: str, value: Any):
        """
        Update an individual print setting.

        :param name: Name of parameter to update
        :param value: Value of parameter to update
        """
        self.config["print_settings"][name] = value
        self.write_config_to_disk()

    def _write_default_config(self):
        # Get default configs from each generator
        default_generator = list(self.generator_defaults.keys())[0]
        default_config = {
            "generator_params": self._get_all_defaults(),
            "generator_pen_maps": {},
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
                    "descr": "Micron 005 Red",
                    "weight": 10,
                    "color": "#eb4034",
                    "location": 3,
                    "pause_to_replace": "true",
                }
            ],
            "current_generator": default_generator,
            "print_settings": {
                "margin_x": 500,
                "margin_y": 500,
                "max_x_coord": 16640,
                "max_y_coord": 10720,
                "scale": 0.5,
                "rotation": 0,
                "translate_x": 0,
                "translate_y": 0,
            },
        }
        self.config = default_config
        self.write_config_to_disk()
