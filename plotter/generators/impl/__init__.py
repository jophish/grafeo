import os
from importlib import import_module

generators = {}

dirname = os.path.dirname(os.path.abspath(__file__))

for f in os.listdir(dirname):
    if (f != "__init__.py" and os.path.isfile("%s/%s" % (dirname, f)) and f[-3:] == ".py"):
        module_name = f[:-3]
        import_module(f".{module_name}", __package__)
        generators[module_name] = getattr(globals()[module_name], module_name)
