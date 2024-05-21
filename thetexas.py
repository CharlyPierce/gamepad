import sys
import select
import time
from evdev import InputDevice, UInput, ecodes as e, AbsInfo
from touchpad_mapper import TouchpadMapper

# Supongamos que los valores mínimos y máximos son conocidos:
touchpad_x_min = 0
touchpad_x_max = 2033
touchpad_y_min = 0
touchpad_y_max = 1332
threshold = 100  # Umbral de movimiento

# Instanciamos la clase TouchpadMapper con los valores mínimos y máximos y el umbral
touchpad_mapper = TouchpadMapper(x_min=0, x_max=2000, y_min=0, y_max=1500, edge_threshold=150, step=600)

# Define el mapeo de teclas del teclado a botones del controlador de Xbox y ejes
key_mapping = {
    e.KEY_W: (e.ABS_Y, -32767),       # Joystick izquierdo arriba
    e.KEY_S: (e.ABS_Y, 32767),        # Joystick izquierdo abajo
    e.KEY_A: (e.ABS_X, -32767),       # Joystick izquierdo izquierda
    e.KEY_D: (e.ABS_X, 32767),        # Joystick izquierdo derecha
    e.KEY_LEFT: (e.ABS_RX, -32767),   # Joystick derecho izquierda
    e.KEY_RIGHT: (e.ABS_RX, 32767),   # Joystick derecho derecha
    e.KEY_UP: (e.ABS_RY, -32767),     # Joystick derecho arriba
    e.KEY_DOWN: (e.ABS_RY, 32767),    # Joystick derecho abajo

    e.KEY_N: e.BTN_TL,                # Botón Superior Izquierdo (LB)
    e.KEY_M: e.BTN_TR,                # Gatillo Derecho (RB)
    e.KEY_J: (e.ABS_Z, 32767),        # Gatillo LT presionado completamente
    e.KEY_K: (e.ABS_RZ, 32767),       # Gatillo RT presionado completamente
    
    e.KEY_0: e.BTN_TR2,               # Start
    e.KEY_LEFTCTRL: e.BTN_TR2,        # Start
    e.KEY_TAB: e.BTN_TL2,             # Select
    e.KEY_LEFTSHIFT: e.BTN_TL2,       # Select

    e.KEY_X:     e.BTN_B,             # B
    e.KEY_SPACE: e.BTN_A,             # A
    e.KEY_E: e.BTN_X,                 # X
    e.KEY_Q: e.BTN_Y,                 # Y


    e.KEY_G: e.BTN_MODE,              # Modo G-Mode//Chat
    
    # D-pad
    e.KEY_KP4: (e.ABS_THROTTLE, -32767), # Botón Izquierda
    e.KEY_KP6: (e.ABS_THROTTLE, 32767),  # Botón Derecha
    e.KEY_KP8: (e.ABS_RUDDER, -32767),   # Botón Arriba
    e.KEY_KP2: (e.ABS_RUDDER, 32767),    # Botón Abajo
}

# Mapea los ejes del joystick derecho y otros botones del controlador de Xbox
cap = {
    e.EV_KEY: [
        e.BTN_Y, e.BTN_A, e.BTN_X, e.BTN_B,
        e.BTN_SELECT, e.BTN_START, e.BTN_MODE,
        e.BTN_TL, e.BTN_TL2, e.BTN_TR, e.BTN_TR2,
        e.BTN_THUMBL, e.BTN_THUMBR
    ],
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RX, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_Y, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_Z, AbsInfo(value=0, min=0, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RZ, AbsInfo(value=0, min=0, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RY, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),

        (e.ABS_THROTTLE, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RUDDER, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
    ]
}

# Crea una instancia de UInput para generar eventos del controlador de juegos virtual
ui = UInput(cap, name='Virtual Xbox Controller', vendor=0x045e, product=0x028e, version=0x0110)

# Define las rutas de los dispositivos de entrada (teclado y touchpad)
keyboard_dev = InputDevice('/dev/input/event0')  # <- Cambiar a tu teclado
touchpad_dev = InputDevice('/dev/input/event4')  # <- Cambiar a tu touchpad

# Variable para rastrear el tiempo de la última interacción
last_interaction_time = time.time()
interaction_timeout = 1  # 1 segundo de inactividad para resetear

def reset_axes():
    for axis in [e.ABS_X, e.ABS_Y, e.ABS_Z, e.ABS_RX, e.ABS_RY, e.ABS_RZ, e.ABS_THROTTLE, e.ABS_RUDDER]:
        ui.write(e.EV_ABS, axis, 0)
    ui.syn()

# Bucle infinito para leer eventos del teclado y touchpad
try:
    devices = {keyboard_dev.fd: keyboard_dev, touchpad_dev.fd: touchpad_dev}
    while True:
        # current_time = time.time()
        # if current_time - last_interaction_time > interaction_timeout:
        #     reset_axes()
        #     last_interaction_time = current_time

        r, w, x = select.select(devices, [], [], 0.5)
        for fd in r:
            dev = devices[fd]
            for event in dev.read():
                last_interaction_time = time.time()  # Actualiza el tiempo de la última interacción
                if dev == keyboard_dev and event.type == e.EV_KEY:
                    # print(f"Evento de teclado: {e.KEY[event.code]} = {'Presionado' if event.value else 'Liberado'}")
                    if event.code in key_mapping:
                        mapping = key_mapping[event.code]
                        if isinstance(mapping, tuple):
                            axis, value = mapping
                            ui.write(e.EV_ABS, axis, value if event.value else 0)
                        else:
                            ui.write(e.EV_KEY, mapping, event.value)
                        ui.syn()
                elif dev == touchpad_dev:
                    if event.type == e.EV_ABS:
                        touchpad_mapper.update(event.code, event.value)
                        x_value, y_value = touchpad_mapper.get_joystick_values()
                        # print(f"{x_value, y_value}")
                        ui.write(e.EV_ABS, e.ABS_X, x_value)      # Joystick izquierdo
                        ui.write(e.EV_ABS, e.ABS_Y, y_value)      # Joystick izquierdo
                        ui.syn()
                    elif event.type == e.EV_KEY:
                        button = 'BTN_TL' if event.code == e.BTN_LEFT else 'BTN_TR'
                        # print(f"Evento de touchpad: Botón {button} {'Presionado' if event.value else 'Liberado'}")
                        if event.code == e.BTN_LEFT:
                            ui.write(e.EV_KEY, e.BTN_TL, event.value)
                        elif event.code == e.BTN_RIGHT:
                            ui.write(e.EV_KEY, e.BTN_TR, event.value)
                        ui.syn()

except KeyboardInterrupt:
    print("Interrupción del programa por el usuario")
finally:
    # Cierra la instancia de UInput
    ui.close()