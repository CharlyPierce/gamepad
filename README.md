# MoltenGamepad Setup Guide

Este repositorio contiene instrucciones para instalar y configurar MoltenGamepad para emular un control de Xbox. Sigue los pasos detallados a continuación.

## Instalación de dependencias

```bash
sudo apt-get update
sudo apt-get install libudev-dev libpthread-stubs0-dev libdlm-dev build-essential
```

## Clonar el repositorio y compilar

```bash
git clone https://github.com/jgeumlek/MoltenGamepad.git
cd MoltenGamepad
```

## Modificar el archivo uinput.h

Abre el archivo `source/core/uinput.h` y añade la siguiente línea:

```cpp
#include <memory>  // Añadir esta línea para incluir la biblioteca de memoria
```

## Modificar el Makefile

Abre el Makefile con tu editor favorito y descomenta las siguientes líneas:

```makefile
MG_BUILT_INS+=wiimote
MG_BUILT_INS+=steamcontroller
MG_BUILT_INS+=example
MG_BUILT_INS+=joycon

#uncomment the lines below to build external plugins to be loaded at run time.
MG_PLUG_INS+=wiimote
MG_PLUG_INS+=steamcontroller
MG_PLUG_INS+=example
MG_PLUG_INS+=joycon
```

## Compilar el proyecto

```bash
make
```

## Configurar udev

```bash
sudo cp ~/MoltenGamepad/installation/systemuser/udev.rulesudev.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Generar archivo de configuración

```bash
./moltengamepad --print-cfg >> ~/.config/moltengamepad/moltengamepad.cfg
```

Establece la siguiente configuración en el archivo:

```plaintext
mimic_xpad = true
```

## Instalar CMake y otras dependencias

```bash
sudo apt-get update
sudo apt-get install cmake make
sudo apt install go-md2man
```

## Descargar y compilar Scrawpp

```bash
git clone https://gitlab.com/dennis-hamester/scrawpp.git
cd scrawpp
cmake .
make
sudo mkdir -p /usr/local/include/scrawpp
sudo cp context.hpp /usr/local/include/scrawpp/
```

## Configurar librerías

Busca la ubicación de la librería `libscraw.so.0` y añade la ruta a tu `LD_LIBRARY_PATH`:

```bash
sudo find / -name "libscraw.so.0"
export LD_LIBRARY_PATH=/path/to/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

## Ejecutar MoltenGamepad

Regresa a la carpeta `MoltenGamepad` y ejecuta:

```bash
./moltengamepad
```

## Permisos al teclado

```bash
sudo usermod -aG input user  # Cambia 'user' por tu nombre de usuario
```

Reinicia tu sistema.

## Ejecutar scripts de Python

```bash
python3 gamepad.py   # Si se tiene touchpad
python3 gamepad_without_tp.py # Si no se tiene touchpad
```

### Configuración de los scripts de Python

En los archivos `gamepad.py` y `gamepad_without_tp.py`, debes cambiar la ruta a tu teclado y al touchpad:

```python
keyboard_dev = InputDevice('/dev/input/event0')  # <- Cambiar a tu teclado
touchpad_dev = InputDevice('/dev/input/event4')  # <- Cambiar a tu touchpad
```

### Localización de dispositivos

Puedes usar \`sudo evtest\` para localizar el dispositivo de tu teclado y tu touchpad.

```bash
sudo evtest
```

¡Listo! Ahora deberías poder emular correctamente el control de Xbox.
