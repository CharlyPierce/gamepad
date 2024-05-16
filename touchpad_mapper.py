import sys
import select
from evdev import InputDevice, UInput, ecodes as e, AbsInfo


class TouchpadMapper:
    def __init__(self, x_min, x_max, y_min, y_max, threshold=50):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_center = ((x_max + x_min) / 2)+ 400
        self.y_center = (y_max + y_min) / 2
        self.current_x = None
        self.current_y = None
        self.threshold = threshold

    def map_touchpad_to_joystick(self, value, center, threshold):
        if value > center + threshold:
            return 32767
        elif value < center - threshold:
            return -32767
        else:
            return 0

    def update(self, code, value):
        if code == e.ABS_X:
            self.current_x = value
        elif code == e.ABS_Y:
            self.current_y = value

    def reset(self):
        self.current_x = None
        self.current_y = None

    def get_joystick_values(self):
        if self.current_x is not None and self.current_y is not None:
            ry_value = self.map_touchpad_to_joystick(self.current_x, self.x_center, self.threshold)
            rz_value = self.map_touchpad_to_joystick(self.current_y, self.y_center, 1.5*self.threshold)
            return ry_value, rz_value
        return 0, 0
