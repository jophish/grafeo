from plotter.generators.impl import generators


class GeneratorManager:
    generators = {}
    current_generator = None

    def __init__(self):
        self._init_generators_with_defaults()

    def get_generator_defaults(self):
        generator_defaults = {}
        for generator_name, generator in self.generators.items():
            generator_defaults[generator_name] = generator.get_default_params()
        return generator_defaults

    def _init_generators_with_defaults(self):
        for generator_name, generator in generators.items():
            self.generators[generator_name] = generator()

    def get_generator_friendly_names(self):
        return [generator.get_friendly_name() for generator in self.generators.values()]

    def set_current_generator(self, generator_name):
        self.current_generator = self.generators[generator_name]

    def set_all_generator_param_values(self, all_generator_param_values):
        for generator_name, param_values in all_generator_param_values.items():
            self.generators[generator_name].set_param_values(param_values)

    def set_current_generator_by_friendly_name(self, friendly_name):
        for generator in self.generators.values():
            if generator.get_friendly_name() == friendly_name:
                self.current_generator = generator
                return
        raise Exception(f'No generator found with friendly name "{friendly_name}"')

    def get_name_by_friendly_name(self, friendly_name):
        for generator_name, generator in self.generators.items():
            if generator.get_friendly_name() == friendly_name:
                return generator_name
        raise Exception(f'No generator found with friendly name "{friendly_name}"')

    def get_current_generator_param_value(self, param_name):
        return self.current_generator.get_param_values()[param_name]

    def get_current_generator_dims(self):
        return self.current_generator.get_dims()

    def generate_current(self):
        return self.current_generator.generate()
