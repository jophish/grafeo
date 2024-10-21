from random import randint
from time import sleep, time

import serial
from serial import EIGHTBITS, PARITY_EVEN, STOPBITS_TWO


def fmt(string):
    return string.encode() + b"\x03"


def read_gpgl(file_path):
    commands = []
    with open(file_path, "r") as f:
        contents = f.read()
        commands = contents.split("\x03")
    return commands


def main_old():
    ser.write(fmt(":"))
    sleep(5)
    ser.write(fmt("M0, 0,"))
    ser.write(fmt("J3"))
    return
    num_bytes = 0
    prev_x = 0
    prev_y = 0

    start_time = time()
    for i in range(50):
        new_x = randint(0, 10000)
        new_y = randint(0, 10000)

        raw_string = f"D{prev_x}, {prev_y}, {new_x}, {new_y}"
        string = fmt(raw_string)

        prev_x = new_x
        prev_y = new_y
        ser.write(string)

        num_bytes += len(string)
        print(raw_string)
        print(num_bytes, i)

        end_time = time()

        print(f"TOTAL TIME: {end_time-start_time}")


def run_prog(gpgl, pen_config):
    ser = serial.Serial(
        port="/dev/ttyUSB0",
        baudrate=9600,
        bytesize=EIGHTBITS,
        parity=PARITY_EVEN,
        stopbits=STOPBITS_TWO,
        timeout=1,
        xonxoff=True,
    )

    ser.write(fmt(":"))
    sleep(5)
    ser.write(fmt("M0, 0"))

    for i in range(len(gpgl)):
        if gpgl[i][:2] == "PR":
            print("Once plotting has paused, please replace pen!")
            new_pen_num = gpgl[i][2]
            new_pen_config = pen_config[str(new_pen_num)]
            print(f'  Pen to load: {new_pen_config["descr"]}')
            print(f'  Slot to load in: {new_pen_config["location"]}')
            ser.write(fmt("J0"))
            input("Press enter to continue")

        ser.write(fmt(gpgl[i]))
        print(f"{round(i/len(gpgl)*100, 2)}%")


def main():
    gpgl = read_gpgl("./gpgl/inkcut-1677023683.gpgl")
    run_prog(gpgl, [])

main()
