from configparser import ConfigParser
from logging import getLogger
import serial_control
import time


logger = getLogger(__name__)


class Rotate_Stepper(object):
    """класс для вращающего барабан шагового двигателя"""

    degrees_config = ConfigParser()
    degrees_config_data = 'src/configs/degrees.conf'
    degrees_config.read(degrees_config_data)

    def __init__(self, mover):
        self.mover = mover
        self.step = int(self.degrees_config['steppers']['step'])
        self.seconds_per_step = int(float(self.degrees_config['steppers']['seconds_per_step']))
        self.buzz_signal_delay = serial_control.buzz_signal_delay

    def add_beg(self, deg) -> int:
        return deg + 360

    def delta_deg(self, beg, end) -> int:
        logger.debug("beg: %i, end: %i", beg, end)
        if end < beg:
            end_ = self.add_beg(end)
            if end_ - beg <= 180:
                return end_ - beg
            else:
                return -(beg - end)
        else:
            if end - beg <= 180:
                return end - beg
            else:
                return -(360 - end)

    def delta_sec(self, degrees) -> float:
        delay_seconds = (abs(degrees) / self.step) * self.seconds_per_step
        return delay_seconds

    def rotate(self, data):
        buzz_delay = self.buzz_signal_delay
        part_name = data.strip("[]'")
        part_name_deg = int(str(self.degrees_config['degrees'][part_name]))

        if part_name_deg == "(no_detections)":
            buzz_delay *= 0

        val = self.delta_deg(beg=serial_control.current_pos, end=part_name_deg)
        logger.info("Part name: %s, target rotate (degrees): %i, left to full turnover: %i", part_name, part_name_deg,
                    val)
        serial_control.current_pos = part_name_deg

        serial_control.serialSend(data=[serial_control.lcd_key, part_name_deg, val])
        serial_control.serialSend(data=[serial_control.rotate_motor_key, buzz_delay, val])
        time.sleep(self.delta_sec(degrees=val))
        self.mover.move(data=self.mover.degrees_per_half_move)
        time.sleep(self.mover.seconds_per_move)
        serial_control.serialSend(data=[serial_control.conveyor_motor_key, serial_control.conveyor_motor_speed])


class Move_Stepper:
    """класс для сдвигающго шагового двигателя"""

    degrees_config_data = 'src/configs/degrees.conf'
    degrees_config = ConfigParser()
    degrees_config.read(degrees_config_data)

    def __init__(self):
        self.seconds_per_move = int(float(self.degrees_config['steppers']['seconds_per_move']))
        self.degrees_per_half_move = int(self.degrees_config['steppers']['degrees_per_half_move'])

    def move(self, data):
        serial_control.serialSend(data=[serial_control.move_motor_key, -data])
        time.sleep(5.5)
        serial_control.serialSend(data=[serial_control.move_motor_key, data])
