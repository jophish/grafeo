from plotter.Repl import Repl
from plotter.config import load_config
def main():
    config = load_config()
    repl = Repl(config['generator_config'], config['pen_config'])
    repl.start_repl()

main()
