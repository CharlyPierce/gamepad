import sys
import select
from evdev import InputDevice, UInput, ecodes as e, AbsInfo



class TouchpadMapper:
    def __init__(self, x_min, x_max, y_min, y_max, edge_threshold=100, step=500):
        # Define los límites del touchpad
        self.x_min = x_min + edge_threshold
        self.x_max = x_max - edge_threshold
        self.y_min = y_min + edge_threshold
        self.y_max = y_max - edge_threshold

        # Define el rango de salida para el joystick y el paso de cambio
        self.joystick_min = -32767
        self.joystick_max = 32767
        self.step = step

        # Variables para almacenar la posición actual detectada en el touchpad
        self.current_x = 0
        self.current_y = 0

    def update(self, code, value):
        # Actualiza las coordenadas actuales basadas en los eventos del touchpad
        if code == e.ABS_X:
            self.current_x = value
        elif code == e.ABS_Y:
            self.current_y = value

    def get_joystick_values(self):
        # Convierte las coordenadas del touchpad a valores de joystick
        x_value = self.map_value(self.current_x, self.x_min, self.x_max, self.joystick_min, self.joystick_max)
        y_value = self.map_value(self.current_y, self.y_min, self.y_max, self.joystick_min, self.joystick_max)
        return x_value, y_value

    def map_value(self, value, input_min, input_max, output_min, output_max):
        # Mapea un valor desde un rango de entrada a un rango de salida
        # Asegura que el valor esté dentro de los límites del touchpad
        value_clamped = max(min(value, input_max), input_min)
        # Calcula el valor proporcional
        proportional_value = output_min + ((value_clamped - input_min) * (output_max - output_min) / (input_max - input_min))
        # Redondea al múltiplo de step más cercano para discretización
        return int(proportional_value // self.step * self.step)