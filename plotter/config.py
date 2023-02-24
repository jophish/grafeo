import json

CONFIG_PATH = './plotter/config.json'

def load_config():
    data = None
    with open(CONFIG_PATH) as json_file:
        data = json.load(json_file)
    return data

def write_config_key(key: str, data: dict):
    new_config = load_config()
    new_config[key] = data
    new_json = json.dumps(new_config)
    with open(CONFIG_PATH, 'w') as json_file:
        json_file.write(new_json)
