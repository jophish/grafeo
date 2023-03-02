import json
import os
from pathlib import Path

CONFIG_FILENAME = "pyplot.json"
CONFIG_PATH = os.path.join(
    Path(os.path.abspath(__file__)).parent.parent.parent.absolute(), CONFIG_FILENAME
)


class ConfigManager:
    def __init__(self, generator_defaults):
        self.generator_defaults = generator_defaults
        self._init_config()

    def _init_config(self):
        if not Path.is_file(Path(CONFIG_PATH)):
            self._write_default_config()
        else:
            self.load_config()

    def load_config(self):
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)

        # If some generator is new and not yet in the config file, we should update the
        # config on disk with the new defaults.
        for generator_name in self.generator_defaults:
            if generator_name not in self.config["generator_params"]:
                self.config["generator_params"][
                    generator_name
                ] = self.generator_defaults[generator_name]
        self.write_config_to_disk()

    def write_config_to_disk(self):
        with open(CONFIG_PATH, "w") as f:
            f.write(json.dumps(self.config, indent=4))

    def get_current_generator(self):
        return self.config["current_generator"]

    def set_current_generator(self, generator_name):
        self.config["current_generator"] = generator_name
        self.write_config_to_disk()

    def set_param_value(self, param_name, param_value):
        current_generator = self.config["current_generator"]
        self.config["generator_params"][current_generator][param_name] = param_value
        self.write_config_to_disk()

    def get_all_generator_param_values(self):
        return self.config["generator_params"]

    def _write_default_config(self):
        # Get default configs from each generator
        default_generator = list(self.generator_defaults.keys())[0]
        default_config = {
            "generator_params": self.generator_defaults,
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
        }
        self.config = default_config
        self.write_config_to_disk()
