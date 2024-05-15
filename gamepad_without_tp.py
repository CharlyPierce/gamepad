import sys
import select
from evdev import InputDevice, UInput, ecodes as e, AbsInfo

# Define el mapeo de teclas del teclado a botones del controlador de Xbox y ejes
key_mapping = {
    e.KEY_W: (e.ABS_Y, -32767),       # Joystick izquierdo arriba
    e.KEY_S: (e.ABS_Y, 32767),        # Joystick izquierdo abajo
    e.KEY_A: (e.ABS_X, -32767),       # Joystick izquierdo izquierda
    e.KEY_D: (e.ABS_X, 32767),        # Joystick izquierdo derecha
    e.KEY_LEFT: (e.ABS_RY, -32767),   # Joystick derecho izquierda
    e.KEY_RIGHT: (e.ABS_RY, 32767),   # Joystick derecho derecha
    e.KEY_UP: (e.ABS_RZ, -32767),     # Joystick derecho arriba
    e.KEY_DOWN: (e.ABS_RZ, 32767),    # Joystick derecho abajo
    e.KEY_I: e.BTN_Y,                 # Botón Y
    e.KEY_K: e.BTN_A,                 # Botón A
    e.KEY_J: e.BTN_X,                 # Botón X
    e.KEY_L: e.BTN_B,                 # Botón B
    e.KEY_2: e.BTN_SELECT,            # Botón Select
    e.KEY_3: e.BTN_START,             # Botón Start
    e.KEY_4: e.BTN_MODE,              # Botón Mode
    e.KEY_8: e.BTN_DPAD_UP,           # DPAD Arriba
    e.KEY_KP2: e.BTN_DPAD_DOWN,       # DPAD Abajo (teclado numérico 2)
    e.KEY_KP6: e.BTN_DPAD_RIGHT,      # DPAD Derecha (teclado numérico 6)
    e.KEY_KP4: e.BTN_DPAD_LEFT,       # DPAD Izquierda (teclado numérico 4)
    e.KEY_Q: e.BTN_TL,                # Gatillo Izquierdo (LT)
    e.KEY_Z: e.BTN_TL2,               # Botón Superior Izquierdo (LB)
    e.KEY_E: e.BTN_TR,                # Gatillo Derecho (RT)
    e.KEY_R: e.BTN_TR2,               # Botón Superior Derecho (RB)
    e.KEY_P: e.BTN_THUMBL,            # Botón del Stick Analógico Izquierdo (ThumbL)
    e.KEY_M: e.BTN_THUMBR,            # Botón del Stick Analógico Derecho (ThumbR)
}

# Mapea los ejes del joystick derecho y otros botones del controlador de Xbox
cap = {
    e.EV_KEY: [
        e.BTN_Y, e.BTN_A, e.BTN_X, e.BTN_B,
        e.BTN_SELECT, e.BTN_START, e.BTN_MODE,
        e.BTN_DPAD_UP, e.BTN_DPAD_DOWN, e.BTN_DPAD_LEFT, e.BTN_DPAD_RIGHT,
        e.BTN_TL, e.BTN_TL2, e.BTN_TR, e.BTN_TR2,
        e.BTN_THUMBL, e.BTN_THUMBR
    ],
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_Y, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_Z, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RZ, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RY, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
    ]
}

# Crea una instancia de UInput para generar eventos del controlador de juegos virtual
ui = UInput(cap, name='Virtual Xbox Controller', vendor=0x045e, product=0x028e, version=0x0110)

# Define la ruta del dispositivo de entrada (teclado)
keyboard_dev = InputDevice('/dev/input/event0')  # <- Cambiar a tu teclado

# Bucle infinito para leer eventos del teclado
try:
    while True:
        r, w, x = select.select([keyboard_dev.fd], [], [])
        for fd in r:
            for event in keyboard_dev.read():
                if event.type == e.EV_KEY:
                    if event.code in key_mapping:
                        mapping = key_mapping[event.code]
                        if isinstance(mapping, tuple):
                            axis, value = mapping
                            ui.write(e.EV_ABS, axis, value if event.value else 0)
                            # if axis == e.ABS_RY:
                                # print(f"Tecla {event.code} mapeada a e.ABS_RY con valor {value}")
                            # elif axis == e.ABS_RZ:
                                # print(f"Tecla {event.code} mapeada a e.ABS_RZ con valor {value}")
                        else:
                            ui.write(e.EV_KEY, mapping, event.value)
                        # Sincroniza los eventos
                        ui.syn()

except KeyboardInterrupt:
    pass  # Maneja la interrupción manual (Ctrl+C)

# Cierra la instancia de UInput
ui.close()
