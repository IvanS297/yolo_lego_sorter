import serial
from configparser import ConfigParser
from logging import getLogger

logger = getLogger()

serial_config_data = 'src/configs/serial.conf'
serial_config = ConfigParser()
serial_config.read(serial_config_data)

COM_PORT = serial_config['serial_connection']['port']
COM_BAUDRATE = int(serial_config['serial_connection']['port_baudrate'])

rotate_motor_key = int(serial_config['keys']['rotate_motor_key'])
move_motor_key = int(serial_config['keys']['move_motor_key'])
conveyor_motor_key = int(serial_config['keys']['conveyor_motor_key'])
lcd_key = int(serial_config['keys']['lcd_key'])

conveyor_motor_speed = int(serial_config['parameters']['conveyor_motor_speed'])
buzz_signal_delay = int(serial_config['parameters']['buzz_signal_delay'])

current_pos = 0
detect_state = False


def init():
    global detect_state


serial_connection = serial.Serial(
    port="\\\\.\\" + COM_PORT,
    baudrate=COM_BAUDRATE,
)


def ClosePort():
    serial_connection.close()


def serialSend(data):
    sending_string = ""
    for val in data:
        sending_string += str(val)
        sending_string += ','
    sending_string = sending_string[:-1]
    sending_string += ';'
    serial_connection.write(sending_string.encode())
    serial_connection.flush()


def onRead():
    while True:
        rx = serial_connection.readline()
        data = str(rx, 'utf-8').strip()
        logger.debug(data)
        data = data.strip("b''").split(',')
        if data[0] == '0':
            global detect_state
            if data[1] == "detected":
                detect_state = True
            else:
                detect_state = False