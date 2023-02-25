from plotter.generators.impl.NoiseLineGenerator import NoiseLineGenerator
from plotter.Sketch import GenSketch
from plotter.ser import run_prog
from plotter.config import load_config, write_config_key
from gpgl import GpglGenerator

class Repl():

    generator_config = {}
    generators = [
        NoiseLineGenerator
    ]

    run_repl = False
    current_generator = None

    commands = {
        'h': 'show help message',
        'lg': 'list generators',
        'sg': 'set generator: sg [n]',
        'lp': 'list parameters of current generator',
        'sp': 'set parameter of current generator: sp [param_shortcode]=[param_value]',
        'g': 'generate using current parameters',
        'ld': 'list default parameters',
        'sd': 'set default parameters',
        'd': 'dump to file: d [filename-suffix]',
        'l': 'load from file: l [filename]',
        'r': 'refresh config from file',
        'q': 'quit',
        'p': 'send to plotter'
    }

    def __init__(self, generator_config, pen_config):
        self.generator_config = generator_config
        self.sketch = GenSketch(generator_config, pen_config)
        self.gpgl_generator = GpglGenerator(generator_config, pen_config)

    def show_help(self):
        for (key, value) in self.commands.items():
            print(f'{key}: {value}')

    def list_generators(self):
        for i in range(len(self.generators)):
            print(f'{i} - {self.generators[i].get_name()}')

    def quit(self):
        print('bye!')
        if self.sketch.is_running:
            self.sketch.exit_sketch()
        self.run_repl = False

    def set_generator(self, gen_num):
        if gen_num >= len(self.generators):
            print(f'please enter a valid generator number {0}-{len(self.generators)-1}')
            return

        if self.current_generator:
            print('overwrite current generator? (y/n)')
            while True:
                print('> ', end='')
                inp = input()
                if inp == 'y':
                    break
                elif inp == 'n':
                    return
                else:
                    print('please enter y or n')

        self.current_generator = self.generators[gen_num](self.generator_config)
        # Load the config file
        self.current_generator.set_param_values(load_config()[self.current_generator.get_name()])
        self.sketch.set_generator(self.current_generator)

    def list_parameters(self):
        if not self.current_generator:
            print('no generator currently defined. set a generator first')
            return
        param_list = self.current_generator.get_param_list()
        param_values = self.current_generator.get_param_values()
        for (param_name, param_info) in param_list.items():
            param_value = param_values[param_name]
            print(f'{param_name} ({param_info[0]}) [{param_info[2]}]: {param_info[1]}')

    def set_parameter(self, param_info):
        if not self.current_generator:
            print('no generator currently defined. set a generator first')
            return
        param_list = self.current_generator.get_param_list()

        param_info_words = param_info.split('=')
        if len(param_info_words) != 2:
            print('sp expects one argument ([param_shortcode]=[param_value])')
            return

        for (param_name, param_info) in param_list.items():
            if param_info[0] == param_info_words[0]:
                try:
                    self.current_generator.set_param_value(param_name, param_info[2](param_info_words[1]))
                except:
                    print('param value not castable to appropriate type')
                return
        print('unknown param shortcode')

    def plot(self):
        if not self.current_generator:
            print('no generator currently defined. set a generator and generate something first')
            return
        lines = self.current_generator.get_lines()
        if not lines:
            print('no gpgl generated. have you generated an image yet?')
            return

        self.gpgl_generator.set_lines(lines)
        gpgl = self.gpgl_generator.generate_gpgl()

        config = load_config()
        print('sending to plotter!')
        run_prog(gpgl, config['pen_config'])

    def generate(self):
        if not self.current_generator:
            print('no generator currently defined. set a generator first')
            return
        try:
            self.current_generator.generate()
        except Exception as e:
            raise e
            print(f'error during generation: {e}')
            return

        if not self.sketch.is_running:
            self.sketch.run_sketch(block=False)
        self.sketch.redraw()

    def refresh(self):
        if not self.current_generator:
            print('no generator currently defined. set a generator first')
            return
        config = load_config()
        self.current_generator.set_param_values(config[self.current_generator.get_name()])
        self.sketch.set_pen_config(config['pen_config'])
        self.gpgl_generator.set_pen_config(config['pen_config'])
        self.generate()

    def process_cmd(self, cmd):
        cmd_words = cmd.split(' ')

        if len(cmd_words) == 0:
            print('please enter a command')
            return

        if cmd_words[0] == 'h':
            self.show_help()
        elif cmd_words[0] == 'lg':
            self.list_generators()
        elif cmd_words[0] == 'sg':
            if len(cmd_words) != 2:
                print('sg expects 1 integer param')
                return
            try:
                self.set_generator(int(cmd_words[1]))
            except:
                print('sg expects 1 integer param')
        elif cmd_words[0] == 'lp':
            self.list_parameters()
        elif cmd_words[0] == 'sp':
            if len(cmd_words) != 2:
                print('sp expects 2 params')
                return
            self.set_parameter(cmd_words[1])
        elif cmd_words[0] == 'g':
            self.generate()
        elif cmd_words[0] == 'p':
            self.plot()
        elif cmd_words[0] == 'r':
            self.refresh()
        elif cmd_words[0] == 'q':
            self.quit()
        else:
            print('unrecognized command')

    def start_repl(self):
        print('hi - type h for help')
        self.run_repl = True

        while self.run_repl:
            print('> ', end='')
            inp = input()
            self.process_cmd(inp)

