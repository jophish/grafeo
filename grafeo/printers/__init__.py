from .GpglPrinter import GpglPrinter

def get_printer(printer_config, serializer):
    if printer_config['serializer'] == 'gpgl':
        return GpglPrinter(serializer)
