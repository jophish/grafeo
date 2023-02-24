from plotter.Repl import Repl

def main():
    generator_config = {
        'width': 16640,
        'height': 10720
    }
    repl = Repl(generator_config)
    repl.start_repl()

main()
