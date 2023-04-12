from plotter.config.ConfigManager import ConfigManager
from plotter.generators.GeneratorManager import GeneratorManager
from plotter.gui.gui import setup_gui

import tracemalloc

tracemalloc.start()

def main():
    """Run the program."""
    generator_manager = GeneratorManager()
    config_manager = ConfigManager(generator_manager.get_generator_defaults())
    generator_manager.set_all_generator_param_values(
        config_manager.get_all_generator_param_values()
    )
    generator_manager.set_current_generator(config_manager.get_current_generator())
    managers = {
        "generator_manager": generator_manager,
        "config_manager": config_manager,
    }
    setup_gui(managers)


main()
