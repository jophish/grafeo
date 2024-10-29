from .Serializer import Serializer
import serial
from serial import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE
from serial import STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
import sys
import glob

class SerialSerializer(Serializer):

    @staticmethod
    def get_available_ports():
        """
        Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        """

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = ['None']
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    @staticmethod
    def get_bytesize(size: int):
        if size == 5:
            return FIVEBITS
        elif size == 6:
            return SIXBITS
        elif size == 7:
            return SEVENBITS
        elif size == 8:
            return EIGHTBITS
        else:
            raise Exception(f'Unknown bytesize {size} for serial port')

    @staticmethod
    def get_parity(parity: str):
        if parity == 'even':
            return PARITY_EVEN
        elif parity == 'none':
            return PARITY_NONE
        elif parity == 'odd':
            return PARITY_ODD
        elif parity == 'mark':
            return PARITY_MARK
        elif parity == 'space':
            return PARITY_SPACE
        else:
            raise Exception(f'Unknown parity {parity} for serial port')

    @staticmethod
    def get_stopbits(stopbits: str):
        if stopbits == '1':
            return STOPBITS_ONE
        elif stopbits == '1.5':
            return STOPBITS_ONE_POINT_FIVE
        elif stopbits == '2':
            return STOPBITS_TWO
        else:
            raise Exception(f'Unknown stopbits {stopbits} for serial port')

    def __init__(self, serial_settings):
        super().__init__()
        bytesize = SerialSerializer.get_bytesize(serial_settings['bytesize'])
        parity = SerialSerializer.get_parity(serial_settings['parity'])
        stopbits= SerialSerializer.get_stopbits(serial_settings['stopbits'])

        xonxoff = serial_settings['flowcontrol'] == 'xon/xoff'
        self.ser = serial.Serial(
            port=serial_settings['port'],
            baudrate=serial_settings['baud'],
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=1,
            xonxoff=xonxoff
        )

    def serialize_command(self, command):
        self.ser.write(command)
