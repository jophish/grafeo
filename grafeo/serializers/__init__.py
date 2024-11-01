from .SerialSerializer import SerialSerializer

def get_serializer(printer_config):
    if printer_config["connection"] == 'serial':
        if printer_config['connection_defaults']['port']:
            return SerialSerializer(printer_config['connection_defaults'])
    return None
