---
document_id: DOC-210
title: "Raspberry Pi, Arduino, and ESP32 Setup and Library Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-210
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Raspberry Pi, Arduino, and ESP32 Setup and Library Guide

210_RASPBERRY_PI_ARDUINO_ESP32_SETUP_AND_LIBRARY_GUIDE
0. Purpose
This document explains how we approach Raspberry Pi, Arduino, ESP32, Pico, and small-controller projects.
It covers:
* which device type is being used;
* how the device talks to a computer;
* which development environment to use;
* how to download the correct board packages and libraries;
* which Python libraries matter on the computer/Raspberry Pi side;
* which Arduino/C++ libraries matter on the microcontroller side;
* which MicroPython/CircuitPython libraries matter;
* how to avoid common compatibility traps;
* how to build repeatable diagnostic procedures.
This document is meant to prevent the same recurring problems:
* downloading the wrong GitHub file;
* installing the wrong board package;
* using the wrong COM port;
* using a charge-only USB cable;
* confusing Raspberry Pi Linux with Raspberry Pi Pico microcontroller behavior;
* mixing Python-on-computer libraries with Arduino-on-device libraries;
* assuming a library works on Windows XP, Raspberry Pi, ESP32, and Pydroid;
* losing data because serial messages were malformed;
* damaging hardware with voltage-level mistakes;
* creating software that only works when everything is connected perfectly.

1. First Distinction: Raspberry Pi vs Pico vs Arduino vs ESP32
A Raspberry Pi 3/4/5/Zero is a small Linux computer. It runs an operating system, usually Raspberry Pi OS. You install Python packages with apt or pip, run scripts, log files, launch GUIs, host servers, and communicate with hardware through GPIO, USB, serial, I2C, SPI, MQTT, sockets, or other protocols.
A Raspberry Pi Pico / Pico W / Pico 2 is a microcontroller board. It does not run Linux and does not use normal Python packages. It is programmed by flashing firmware/code to the board, typically using MicroPython, C/C++, or CircuitPython-style workflows. Raspberry Pi’s documentation describes Pico boards as microcontroller boards programmed by flashing binaries to onboard flash memory rather than running Linux. (Raspberry Pi)
An Arduino board is a microcontroller board typically programmed in Arduino C/C++ using Arduino IDE, Arduino CLI, or PlatformIO.
An ESP32 is a Wi-Fi/Bluetooth-capable microcontroller family from Espressif. It can be programmed with Arduino C++, ESP-IDF, MicroPython, CircuitPython, or PlatformIO. Espressif maintains the Arduino core for ESP32; its current documentation covers Arduino-ESP32 core 3.3.8 based on ESP-IDF 5.5 as of the accessed docs. (Espressif Systems)
Core rule:
Raspberry Pi computer:
    Python/Linux project.

Raspberry Pi Pico:
    MicroPython/CircuitPython/C/C++ microcontroller project.

Arduino:
    Arduino C/C++ microcontroller project.

ESP32:
    Arduino C++, ESP-IDF, MicroPython, or CircuitPython microcontroller project.

Do not choose libraries until the device category is clear.

2. Standard Project Roles
Many of our projects use one of these structures.
2.1 Raspberry Pi as the main controller
Sensors / Arduino / ESP32 / LabJack / instruments
        ↓
Raspberry Pi
        ↓
Python GUI / logger / database / MQTT / local server
        ↓
CSV / SQLite / plots / diagnostics

Use this when the Pi is doing:
* data logging;
* graphing;
* touchscreen UI;
* device coordination;
* local web server;
* MQTT broker/client;
* serial hub;
* LabJack communication;
* file storage;
* diagnostics.
2.2 Arduino or ESP32 as a sensor node
Sensor
    ↓
Arduino / ESP32
    ↓
USB Serial / UART / Wi-Fi / MQTT
    ↓
Raspberry Pi or PC
    ↓
Python logger / GUI / database

Use this when the microcontroller is close to the sensor or needs real-time I/O.
2.3 ESP32 as a wireless node
Sensor
    ↓
ESP32
    ↓
Wi-Fi / MQTT / HTTP / UDP
    ↓
Raspberry Pi / PC / local server

Use this when wiring back to the main computer is inconvenient.
2.4 Pico as a simple embedded controller
Sensor / output
    ↓
Pico / Pico W
    ↓
USB serial / UART / Wi-Fi if Pico W
    ↓
PC or Raspberry Pi

Use this for low-cost deterministic embedded logic.

3. Computer-Side vs Device-Side Libraries
A common mistake is mixing these categories.
3.1 Computer-side Python libraries
These run on:
Windows PC
Raspberry Pi Linux
Linux laptop
modern macOS
sometimes Pydroid

Examples:
pyserial
paho-mqtt
gpiozero
lgpio
pigpio
numpy
matplotlib
sqlite3
Flask
PyQt

3.2 Arduino/ESP32 device-side C++ libraries
These are installed in:
Arduino IDE
Arduino CLI
PlatformIO

Examples:
ArduinoJson
PubSubClient
WiFi
Wire
SPI
Adafruit_Sensor
OneWire
DallasTemperature
Adafruit_BME280
Adafruit_ADS1X15

3.3 MicroPython device-side modules
These run on:
ESP32 with MicroPython firmware
Raspberry Pi Pico with MicroPython firmware

Examples:
machine
time
network
urequests
ujson
umqtt.simple
ssd1306
neopixel
dht

MicroPython is a Python 3 implementation for embedded hardware; the official MicroPython documentation provides platform-specific references including ESP32 and RP2/Pico-family ports. (MicroPython Documentation)
3.4 CircuitPython / Blinka libraries
CircuitPython libraries may run:
on CircuitPython microcontroller firmware
or on Raspberry Pi Linux through Adafruit Blinka

Adafruit documents Blinka as the compatibility layer that allows CircuitPython libraries to run on supported Linux systems such as Raspberry Pi; their guide notes that Blinka currently requires Python 3.7+ and Raspberry Pi OS Bullseye or newer. (Adafruit Learning System)

4. Standard Setup Decision Tree
What board is this?

Raspberry Pi 3/4/5/Zero:
    Use Raspberry Pi OS.
    Use Python 3.
    Install packages with apt first, pip second.
    Use GPIO Zero / lgpio / pigpio / Blinka as appropriate.

Raspberry Pi Pico / Pico W / Pico 2:
    Choose MicroPython, CircuitPython, or C/C++.
    Use Thonny for simplest MicroPython workflow.
    Use USB serial/REPL for debugging.

Arduino Uno/Nano/Mega/etc.:
    Use Arduino IDE or Arduino CLI.
    Install board support if not built in.
    Install libraries through Library Manager or arduino-cli.

ESP32:
    Choose Arduino core, ESP-IDF, PlatformIO, MicroPython, or CircuitPython.
    For Arduino-style work, install Espressif ESP32 board support.
    For MicroPython, flash MicroPython firmware with esptool or Thonny-style tools.

Need a PC/Raspberry Pi to talk to the board?
    Use pyserial, MQTT, HTTP, sockets, or file transfer depending on project.

5. USB Cable, Drivers, and Ports
Before debugging code, verify the physical connection.
5.1 USB cable rule
Many USB cables are charge-only.
If the board powers on but no serial port appears, try a known data-capable USB cable.
5.2 Common USB-serial chips
Many Arduino/ESP32 boards use one of these USB-to-UART chips:
CP210x
CH340 / CH341
FTDI
native USB microcontroller

Silicon Labs provides CP210x Virtual COM Port drivers for CP210x USB-to-UART bridge devices, and FTDI provides VCP drivers that make FTDI devices appear as standard COM ports to PC software. (Silicon Labs)
WCH provides CH341/CH340 driver downloads; many low-cost Arduino-compatible boards use CH340/CH341 USB-serial chips. (WCH Microelectronics)
5.3 Windows COM port check
Open Device Manager:
Ports (COM & LPT)
Universal Serial Bus controllers
Other devices

Look for:
USB Serial Device (COMx)
Silicon Labs CP210x USB to UART Bridge
USB-SERIAL CH340
FTDI USB Serial Port
Arduino Uno

5.4 Linux/Raspberry Pi serial check
ls /dev/ttyUSB*
ls /dev/ttyACM*
dmesg | tail -50

Common port names:
/dev/ttyUSB0
/dev/ttyACM0

5.5 Python serial port scan
import serial.tools.list_ports

for port in serial.tools.list_ports.comports():
    print(port.device, port.description, port.hwid)

Install pyserial:
python -m pip install pyserial

or on Raspberry Pi:
python3 -m pip install pyserial

6. Raspberry Pi Linux Setup
6.1 Basic system check
Run:
uname -a
cat /etc/os-release
python3 --version
python3 -m pip --version

6.2 Update package lists
sudo apt update

Optional upgrade:
sudo apt upgrade

6.3 Install common base packages
sudo apt install -y python3-pip python3-venv python3-tk git

For serial work:
sudo apt install -y python3-serial

For plotting:
sudo apt install -y python3-matplotlib python3-numpy

For I2C tools:
sudo apt install -y i2c-tools

For SQLite:
sudo apt install -y sqlite3

6.4 Use apt first for hardware/system packages
On Raspberry Pi, prefer:
apt for system/hardware-integrated packages
pip for project-local pure Python or application-level packages

This is especially important for GPIO, camera, OpenCV, and packages with native dependencies.
6.5 Virtual environments
Modern Raspberry Pi OS may discourage system-wide pip installs. Use a project venv:
mkdir my_project
cd my_project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

For GPIO packages already installed system-wide, a venv may need system site packages:
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

This is often relevant because GPIO libraries are tied to OS-level packages and device access.

7. Raspberry Pi GPIO Libraries
7.1 Recommended default: gpiozero
GPIO Zero is a friendly Python API for Raspberry Pi GPIO and is installed by default in the Raspberry Pi OS desktop image according to its documentation. The docs also note installation paths for Raspberry Pi OS Lite and other systems. (gpiozero)
Install if needed:
sudo apt install -y python3-gpiozero

Basic LED test:
from gpiozero import LED
from time import sleep

led = LED(17)

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)

Basic button test:
from gpiozero import Button
from signal import pause

button = Button(2)

button.when_pressed = lambda: print("pressed")
button.when_released = lambda: print("released")

pause()

Use gpiozero when:
* controlling LEDs, buttons, relays, buzzers;
* doing simple GPIO logic;
* teaching or prototyping;
* wanting readable code.
7.2 lgpio
lgpio is the lower-level GPIO library often used under the hood on newer Raspberry Pi OS / Pi 5-era setups. Prefer using it through GPIO Zero unless lower-level control is required.
Install:
sudo apt install -y python3-lgpio

7.3 pigpio
pigpio is useful for more advanced GPIO timing, servo/PWM work, remote GPIO, and daemon-based control.
Install:
sudo apt install -y pigpio python3-pigpio

Start daemon:
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

Python example:
import pigpio
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon not connected")

PIN = 18
pi.set_mode(PIN, pigpio.OUTPUT)
pi.write(PIN, 1)
time.sleep(1)
pi.write(PIN, 0)
pi.stop()

7.4 RPi.GPIO
RPi.GPIO exists in many older projects, but it should not be the default for new work. It is not the Raspberry Pi organization’s current recommended high-level path, and Raspberry Pi 5 / Bookworm-era GPIO changes have made old assumptions unreliable. Raspberry Pi forum discussions from Raspberry Pi staff/community repeatedly point users toward GPIO Zero for current Python GPIO workflows and note Pi 5 compatibility complications for older GPIO libraries. (Raspberry Pi Forums)
Use RPi.GPIO only when:
old project already depends on it
target Pi/OS version is known-good
rewriting is not currently worth it

Do not use it as the default for new Pi 5 / Bookworm projects.

8. Raspberry Pi I2C, SPI, and Hardware Interfaces
8.1 Enable interfaces
Use:
sudo raspi-config

Then:
Interface Options
    I2C
    SPI
    Serial Port

Or edit configuration depending on OS version.
8.2 I2C scan
Install:
sudo apt install -y i2c-tools

Scan bus 1:
i2cdetect -y 1

Common I2C addresses:
0x40 INA219 / some sensors
0x48 ADS1115
0x76 / 0x77 BME280/BMP280
0x3C OLED display

8.3 Common Raspberry Pi Python hardware libraries
gpiozero
    Friendly high-level GPIO.

lgpio
    Lower-level GPIO backend, important on newer Raspberry Pi systems.

pigpio
    Daemon-based GPIO, PWM, timing, servo, remote GPIO.

smbus2
    I2C communication from Python.

spidev
    SPI communication from Python.

pyserial
    USB serial / UART communication.

paho-mqtt
    MQTT messaging for distributed sensor networks.

adafruit-blinka
    CircuitPython compatibility layer for Raspberry Pi Linux.

adafruit-circuitpython-*
    Sensor/display/motor libraries usable through Blinka.

RPi.GPIO
    Legacy GPIO library; avoid as default for new work.

Install examples:
sudo apt install -y python3-smbus python3-spidev
python3 -m pip install smbus2 paho-mqtt

Blinka:
python3 -m pip install Adafruit-Blinka

Adafruit’s Blinka docs show PyPI installation patterns and virtual-environment installation patterns for Raspberry Pi-style Linux systems. (CircuitPython Documentation)

9. Raspberry Pi DAQ / Logger Recommended Python Stack
For our DAQ/logger/touchscreen/SQLite projects:
Required / common:
    pyserial
    paho-mqtt
    numpy
    matplotlib
    sqlite3
    csv
    queue
    threading
    json
    logging
    gpiozero

Optional:
    PyQt5 or Tkinter
    psutil
    smbus2
    spidev
    adafruit-blinka
    adafruit-circuitpython-*
    pigpio
    Flask
    pyzmq

Install conservative subset:
sudo apt install -y python3-pip python3-numpy python3-matplotlib python3-tk python3-serial sqlite3
python3 -m pip install paho-mqtt psutil

If using a venv:
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install paho-mqtt psutil

10. Arduino IDE Setup
Use Arduino IDE when:
* the user wants a graphical interface;
* installing libraries through Library Manager;
* selecting boards/ports manually;
* uploading sketches interactively.
Arduino’s documentation says libraries can be installed through the IDE Library Manager via the Sketch menu, and Arduino CLI provides command-line Boards/Library Managers, sketch builder, board detection, and uploader functionality. (Arduino)
10.1 Install a library in Arduino IDE
Arduino IDE
    → Sketch
    → Include Library
    → Manage Libraries
    → Search library name
    → Install

10.2 Install a board package
Arduino IDE
    → Tools
    → Board
    → Boards Manager
    → Search board/core
    → Install

For ESP32, install the Espressif ESP32 board support package using Arduino IDE, Arduino CLI, PlatformIO, or manual install methods described by Espressif’s Arduino-ESP32 documentation. (Espressif Systems)

11. Arduino CLI Setup
Use Arduino CLI when:
* building repeatable packages;
* compiling from scripts;
* working headless;
* documenting exact commands;
* creating deterministic build instructions.
11.1 Check Arduino CLI
arduino-cli version

11.2 Initialize config
arduino-cli config init

11.3 Update core/library index
arduino-cli core update-index
arduino-cli lib update-index

11.4 List connected boards
arduino-cli board list

11.5 Search libraries
arduino-cli lib search "ArduinoJson"

11.6 Install libraries
Arduino CLI’s lib install command installs one or more libraries and accepts version pins with LIBRARY@VERSION_NUMBER. (Arduino)
arduino-cli lib install ArduinoJson
arduino-cli lib install PubSubClient
arduino-cli lib install "Adafruit BME280 Library"

Version-pinned example:
arduino-cli lib install ArduinoJson@6.21.5

11.7 Install board core
Arduino AVR:
arduino-cli core install arduino:avr

ESP32:
arduino-cli core install esp32:esp32

11.8 Compile
arduino-cli compile --fqbn arduino:avr:uno MySketch

ESP32 example:
arduino-cli compile --fqbn esp32:esp32:esp32 MySketch

11.9 Upload
arduino-cli upload -p COM5 --fqbn arduino:avr:uno MySketch

Linux:
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno MySketch

ESP32:
arduino-cli upload -p COM5 --fqbn esp32:esp32:esp32 MySketch

12. Arduino / ESP32 C++ Libraries We Commonly Need
12.1 Core communication
Serial
    Built-in Arduino serial communication.

Wire
    Built-in I2C communication.

SPI
    Built-in SPI communication.

WiFi
    ESP32 Wi-Fi library included with ESP32 Arduino core.

WiFiClient
    TCP client support for ESP32 networking.

WebServer / ESPAsyncWebServer
    Local web server on ESP32.

HTTPClient
    ESP32 HTTP requests.

PubSubClient
    MQTT client, common for ESP32/Arduino sensor nodes.

ArduinoJson
    JSON parsing/serialization for structured messages.

Install examples:
arduino-cli lib install ArduinoJson
arduino-cli lib install PubSubClient

12.2 Sensors
Adafruit Unified Sensor
    Common abstraction dependency for many Adafruit sensor libraries.

Adafruit BME280 Library
    Temperature, humidity, pressure sensor.

Adafruit BMP280 Library
    Pressure/temperature sensor.

Adafruit ADS1X15
    ADS1015/ADS1115 external ADCs.

DHT sensor library
    DHT11/DHT22 temperature/humidity sensors.

OneWire
    OneWire bus support.

DallasTemperature
    DS18B20 temperature sensors over OneWire.

Adafruit INA219
    Current/voltage/power monitor.

Adafruit MAX31855 / MAX31856
    Thermocouple amplifier libraries.

Adafruit MCP23017
    I/O expander over I2C.

Adafruit NeoPixel
    WS2812/NeoPixel LED strips.

Install examples:
arduino-cli lib install "Adafruit Unified Sensor"
arduino-cli lib install "Adafruit BME280 Library"
arduino-cli lib install "Adafruit ADS1X15"
arduino-cli lib install "DHT sensor library"
arduino-cli lib install OneWire
arduino-cli lib install DallasTemperature
arduino-cli lib install "Adafruit INA219"
arduino-cli lib install "Adafruit NeoPixel"

12.3 Displays
Adafruit GFX Library
    Common graphics base library.

Adafruit SSD1306
    OLED displays.

U8g2
    Broad monochrome display support.

LiquidCrystal
    Standard character LCD support.

TFT_eSPI
    ESP32/ESP8266 TFT display library.

Install:
arduino-cli lib install "Adafruit GFX Library"
arduino-cli lib install "Adafruit SSD1306"
arduino-cli lib install U8g2
arduino-cli lib install TFT_eSPI

12.4 Timing, control, and storage
TimerOne
    Timer interrupts on AVR boards.

Ticker
    Timing callbacks, often used on ESP boards.

Servo / ESP32Servo
    Servo control.

AccelStepper
    Stepper motor control.

PID_v1
    Simple PID control.

Preferences
    ESP32 nonvolatile key/value storage.

EEPROM
    EEPROM-style persistent storage.

SD
    SD card access.

LittleFS / SPIFFS
    On-device flash filesystem for ESP32.

Install:
arduino-cli lib install AccelStepper
arduino-cli lib install PID
arduino-cli lib install ESP32Servo

Some libraries are board-core built-ins rather than Library Manager installs.

13. ESP32 Arduino Setup
13.1 Arduino IDE method
Arduino IDE
    → Boards Manager
    → Search "esp32"
    → Install "esp32 by Espressif Systems"

Then select board:
Tools → Board → esp32 → your board

Common board choices:
ESP32 Dev Module
ESP32-WROOM-DA Module
ESP32-S3 Dev Module
ESP32-C3 Dev Module
Heltec WiFi LoRa 32

Use the exact board if known; otherwise start with a generic dev module.
13.2 Arduino CLI method
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli board listall | grep -i esp32

Compile:
arduino-cli compile --fqbn esp32:esp32:esp32 MySketch

Upload:
arduino-cli upload -p COM5 --fqbn esp32:esp32:esp32 MySketch

13.3 ESP32 upload troubleshooting
Common issues:
Wrong COM port.
Charge-only USB cable.
Missing CP210x/CH340/FTDI driver.
Board not in bootloader mode.
Wrong board selected.
Wrong upload speed.
Serial monitor already open.
Another program owns the port.

Try:
Hold BOOT while upload starts.
Tap EN/RESET if upload stalls.
Lower upload speed.
Close Serial Monitor before uploading.
Try another cable.
Check Device Manager or /dev/ttyUSB*.

14. PlatformIO Setup
Use PlatformIO when:
* project has many source files;
* libraries need version pinning;
* builds must be repeatable;
* VS Code workflow is acceptable;
* ESP32/Arduino projects are growing beyond one .ino file.
PlatformIO provides framework support for Arduino-style projects and has documentation for Arduino framework usage and installation. (PlatformIO Documentation)
Example platformio.ini:
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200

lib_deps =
    bblanchon/ArduinoJson
    knolleary/PubSubClient
    adafruit/Adafruit BME280 Library
    adafruit/Adafruit Unified Sensor

Build:
pio run

Upload:
pio run --target upload

Monitor:
pio device monitor

Use PlatformIO when exact library/core versions matter and the project is no longer a quick prototype.

15. MicroPython Setup for ESP32 and Pico
15.1 When to choose MicroPython
Use MicroPython when:
* you want Python-like code directly on ESP32/Pico;
* the project is small or medium complexity;
* fast iteration matters;
* REPL debugging is useful;
* you do not need the full Arduino ecosystem.
Do not choose MicroPython when:
* timing is extremely tight;
* a required Arduino C++ library has no MicroPython equivalent;
* memory is very constrained;
* complex Wi-Fi/Bluetooth library support is needed and only exists in Arduino/ESP-IDF form.
15.2 Pico MicroPython with Thonny
Raspberry Pi’s Pico MicroPython documentation points users to Thonny and command-line workflows for connecting to Pico boards and programming them in MicroPython. (Raspberry Pi)
Basic flow:
Install Thonny.
Connect Pico while holding BOOTSEL if flashing firmware.
Install/select MicroPython firmware.
Choose MicroPython interpreter.
Save code as main.py on the device if it should auto-run.

15.3 ESP32 MicroPython with esptool
Espressif documents esptool as a Python-based, platform-independent utility for flashing, provisioning, and interacting with Espressif SoCs. (Espressif Systems)
Install:
python -m pip install esptool

Erase flash:
python -m esptool --chip esp32 --port COM5 erase_flash

Linux:
python -m esptool --chip esp32 --port /dev/ttyUSB0 erase_flash

Write MicroPython firmware:
python -m esptool --chip esp32 --port COM5 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-xxxx.bin

The exact firmware filename depends on the board/firmware downloaded from MicroPython.
15.4 MicroPython serial tools
Install:
python -m pip install mpremote

List/connect:
mpremote

Copy file:
mpremote cp main.py :main.py

Run file:
mpremote run main.py

REPL:
mpremote repl

16. MicroPython Modules We Commonly Use
machine
    Pins, ADC, PWM, I2C, SPI, UART, timers.

time
    Sleeps, ticks, timing loops.

network
    Wi-Fi on ESP32/Pico W.

socket
    TCP/UDP networking.

urequests
    HTTP requests on MicroPython.

ujson
    JSON parsing/serialization.

umqtt.simple
    Simple MQTT client.

neopixel
    WS2812/NeoPixel LEDs.

dht
    DHT11/DHT22 sensors.

ssd1306
    OLED display driver.

onewire
    OneWire bus.

ds18x20
    DS18B20 temperature sensors.

ubluetooth
    Bluetooth BLE support on some ports.

os
    Filesystem operations on device flash.

sys
    Runtime info and path/module behavior.

Example blink:
from machine import Pin
from time import sleep

led = Pin(2, Pin.OUT)

while True:
    led.value(1)
    sleep(1)
    led.value(0)
    sleep(1)

ESP32 Wi-Fi skeleton:
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SSID", "PASSWORD")

for _ in range(20):
    if wlan.isconnected():
        break
    time.sleep(0.5)

print(wlan.ifconfig())

UART example:
from machine import UART
import time

uart = UART(1, baudrate=115200, tx=17, rx=16)

while True:
    uart.write("hello\n")
    time.sleep(1)

17. CircuitPython / Blinka
17.1 When to use CircuitPython libraries
Use CircuitPython libraries when:
* using Adafruit sensors/displays;
* using Raspberry Pi Linux with Blinka;
* wanting consistent driver APIs across boards;
* the hardware driver already exists in the Adafruit ecosystem.
17.2 Raspberry Pi Blinka install
python3 -m pip install Adafruit-Blinka

Sensor example dependencies:
python3 -m pip install adafruit-circuitpython-bme280
python3 -m pip install adafruit-circuitpython-ads1x15
python3 -m pip install adafruit-circuitpython-ina219
python3 -m pip install adafruit-circuitpython-ssd1306

Example:
import board
import busio
import adafruit_bme280.basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)

print(sensor.temperature)
print(sensor.humidity)
print(sensor.pressure)

17.3 Common Blinka/CircuitPython libraries
Adafruit-Blinka
    Compatibility layer for running CircuitPython libraries on Linux boards.

adafruit-circuitpython-bme280
    BME280 temp/humidity/pressure.

adafruit-circuitpython-bmp280
    BMP280 pressure/temp.

adafruit-circuitpython-ads1x15
    ADS1015/ADS1115 ADCs.

adafruit-circuitpython-ina219
    Current/voltage monitor.

adafruit-circuitpython-ssd1306
    OLED display.

adafruit-circuitpython-mcp230xx
    MCP23017 I/O expanders.

adafruit-circuitpython-neopixel
    NeoPixel LEDs.

adafruit-circuitpython-dht
    DHT sensors.

adafruit-circuitpython-max31855
    Thermocouple amplifier.

18. Serial Protocol Rules for Our Projects
When Arduino/ESP32/Pico sends data to Raspberry Pi/PC, use structured lines.
18.1 Bad serial output
23.1,50.2
temp is 23.1
hello
error maybe

This becomes hard to parse and easy to corrupt.
18.2 Better serial output
DATA,device_id,timestamp_ms,seq,temp_c,humidity_pct
DATA,esp32_01,123456,42,23.10,50.20

18.3 JSON line option
{"type":"data","device":"esp32_01","seq":42,"temp_c":23.1,"humidity_pct":50.2}

18.4 Required message fields
type
device_id
sequence_number
measurement_timestamp
values
units or implied schema
status / quality
checksum if needed

18.5 Python receiver skeleton
import serial
import json
import time

PORT = "COM5"      # or "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

while True:
    line = ser.readline().decode("utf-8", "replace").strip()
    if not line:
        continue

    try:
        msg = json.loads(line)
    except Exception:
        print("BAD LINE:", line)
        continue

    if msg.get("type") != "data":
        print("EVENT:", msg)
        continue

    received_at = time.time()
    print(received_at, msg)

18.6 Arduino JSON sender skeleton
#include <ArduinoJson.h>

unsigned long seq = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  StaticJsonDocument<256> doc;

  doc["type"] = "data";
  doc["device"] = "arduino_01";
  doc["seq"] = seq++;
  doc["timestamp_ms"] = millis();
  doc["temp_c"] = 23.1;

  serializeJson(doc, Serial);
  Serial.println();

  delay(1000);
}

Required Arduino library:
arduino-cli lib install ArduinoJson

19. MQTT Pattern for ESP32 / Raspberry Pi
Use MQTT when:
* there are multiple wireless nodes;
* Raspberry Pi is acting as central logger;
* messages can tolerate network latency;
* a pub/sub pattern is cleaner than direct serial.
19.1 Raspberry Pi broker
Install Mosquitto:
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

19.2 Python MQTT client
Install:
python3 -m pip install paho-mqtt

Subscriber:
import json
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", "replace")
    try:
        data = json.loads(payload)
    except Exception:
        print("Bad MQTT payload:", payload)
        return
    print(msg.topic, data)

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("sensors/#")
client.loop_forever()

19.3 ESP32 Arduino MQTT libraries
arduino-cli lib install PubSubClient
arduino-cli lib install ArduinoJson

ESP32 publishes JSON to:
sensors/esp32_01/data

20. Voltage-Level and Wiring Rules
20.1 Logic levels
Raspberry Pi GPIO:
    3.3 V only, not 5 V tolerant.

ESP32 GPIO:
    3.3 V logic, not 5 V tolerant.

Arduino Uno/Nano classic:
    commonly 5 V logic.

Arduino Due / some newer boards:
    3.3 V logic.

Pico:
    3.3 V logic, not 5 V tolerant.

20.2 UART wiring
TX device A → RX device B
RX device A ← TX device B
GND device A ↔ GND device B

If one side is 5 V and the other is 3.3 V, use a level shifter or voltage divider where needed.
20.3 Never do this
Arduino Uno 5 V TX directly into Raspberry Pi RX.
Arduino Uno 5 V TX directly into ESP32 RX.
5 V signal directly into Pico GPIO.

20.4 Always document wiring
WIRE-001
Signal:
Source device:
Source pin:
Source voltage:
Destination device:
Destination pin:
Destination voltage tolerance:
Level shifter used? Yes/No:
Common ground? Yes/No:
Verified by:
Date:

21. Recommended Library Sets by Project Type
21.1 Raspberry Pi DAQ logger
Computer-side:
python3
pyserial
paho-mqtt
numpy
matplotlib
sqlite3
csv
gpiozero
psutil

Optional:
PyQt5
Tkinter
Flask
pyzmq
smbus2
spidev
Adafruit-Blinka

Install:
sudo apt install -y python3-pip python3-venv python3-numpy python3-matplotlib python3-serial python3-tk sqlite3
python3 -m pip install paho-mqtt psutil

21.2 Raspberry Pi GPIO controller
gpiozero
lgpio
pigpio

Install:
sudo apt install -y python3-gpiozero python3-lgpio pigpio python3-pigpio

21.3 Arduino sensor node
Arduino-side:
ArduinoJson
Adafruit Unified Sensor
Adafruit BME280 Library
Adafruit ADS1X15
DHT sensor library
OneWire
DallasTemperature

Install:
arduino-cli lib install ArduinoJson
arduino-cli lib install "Adafruit Unified Sensor"
arduino-cli lib install "Adafruit BME280 Library"
arduino-cli lib install "Adafruit ADS1X15"
arduino-cli lib install "DHT sensor library"
arduino-cli lib install OneWire
arduino-cli lib install DallasTemperature

21.4 ESP32 Wi-Fi sensor node
Arduino-side:
WiFi
PubSubClient
ArduinoJson
Preferences
WebServer or ESPAsyncWebServer
Adafruit sensor libraries as needed

Install:
arduino-cli core install esp32:esp32
arduino-cli lib install PubSubClient
arduino-cli lib install ArduinoJson

21.5 ESP32 MicroPython node
Device-side:
machine
network
time
ujson
umqtt.simple
urequests
ssd1306
dht
neopixel

Computer-side:
esptool
mpremote
pyserial

Install:
python -m pip install esptool mpremote pyserial

21.6 Pico MicroPython project
Device-side:
machine
time
rp2
network, if Pico W
ujson

Computer-side:
Thonny
mpremote
pyserial

Install:
python -m pip install mpremote pyserial

22. Windows / PowerShell / Command Prompt Quick Commands
22.1 Check Python
python --version
python -m pip --version

22.2 List serial ports with Python
python - << "PY"
import serial.tools.list_ports
for p in serial.tools.list_ports.comports():
    print(p.device, p.description)
PY

If PowerShell redirection gives trouble, put this in list_ports.py:
import serial.tools.list_ports

for p in serial.tools.list_ports.comports():
    print(p.device, p.description, p.hwid)

Run:
python list_ports.py

22.3 Arduino CLI board list
arduino-cli board list

22.4 Serial monitor with Arduino CLI
arduino-cli monitor -p COM5

23. Raspberry Pi / Linux Quick Commands
23.1 List serial devices
ls /dev/ttyUSB*
ls /dev/ttyACM*

23.2 Monitor serial
Install:
sudo apt install -y minicom

Run:
minicom -D /dev/ttyUSB0 -b 115200

Or use Python.
23.3 Add user to dialout
sudo usermod -a -G dialout $USER

Then log out/in or reboot.
23.4 I2C scan
i2cdetect -y 1

24. Diagnostics Script for Computer ↔ Board Projects
Save as:
tools/embedded_link_diagnostic.py

import os
import sys
import time
import platform
import subprocess

def try_import(name):
    try:
        __import__(name)
        return "PASS"
    except Exception as exc:
        return "FAIL: %r" % exc

print("Embedded Link Diagnostic")
print("=" * 72)
print("timestamp:", time.strftime("%Y-%m-%d %H:%M:%S"))
print("python:", sys.version)
print("executable:", sys.executable)
print("platform:", platform.platform())
print("cwd:", os.getcwd())
print("")

print("Import checks")
print("-" * 72)
for mod in ["serial", "paho.mqtt.client", "gpiozero", "lgpio", "pigpio", "numpy", "matplotlib"]:
    print(mod, try_import(mod))

print("")
print("Serial ports")
print("-" * 72)
try:
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
    for p in ports:
        print(p.device, "|", p.description, "|", p.hwid)
except Exception as exc:
    print("Serial port scan failed:", repr(exc))

print("")
print("Arduino CLI")
print("-" * 72)
try:
    out = subprocess.check_output(["arduino-cli", "version"], stderr=subprocess.STDOUT)
    print(out.decode("utf-8", "replace"))
except Exception as exc:
    print("arduino-cli unavailable:", repr(exc))

print("")
print("esptool")
print("-" * 72)
try:
    out = subprocess.check_output([sys.executable, "-m", "esptool", "version"], stderr=subprocess.STDOUT)
    print(out.decode("utf-8", "replace"))
except Exception as exc:
    print("esptool unavailable:", repr(exc))

25. Standard Troubleshooting Checklist
25.1 Board not detected
[ ] Data-capable USB cable used.
[ ] Board powers on.
[ ] Correct driver installed.
[ ] Device appears in Device Manager or /dev.
[ ] Serial monitor closed before upload.
[ ] Correct board selected.
[ ] Correct port selected.
[ ] Tried BOOT/RESET sequence for ESP32.
[ ] Tried lower upload speed.
[ ] Tried different USB port.

25.2 Code uploads but nothing works
[ ] Serial baud rate matches code.
[ ] Pins match actual wiring.
[ ] Sensor power voltage correct.
[ ] Common ground connected.
[ ] I2C address verified.
[ ] GPIO numbering convention checked.
[ ] Logic-level compatibility checked.
[ ] Library example sketch tested first.

25.3 Raspberry Pi GPIO not working
[ ] Correct OS version recorded.
[ ] Correct Pi model recorded.
[ ] gpiozero installed.
[ ] lgpio installed if needed.
[ ] Not relying on old RPi.GPIO assumptions.
[ ] Pin numbering clear: BCM vs physical pin.
[ ] User has permission / running normal Python shell.
[ ] Tested minimal LED/button script.

25.4 Serial data corrupted
[ ] Baud rate matches both sides.
[ ] Messages are newline-delimited.
[ ] No debug text mixed with data protocol.
[ ] Packet has type/device/sequence fields.
[ ] Receiver validates field count or JSON.
[ ] Bad packets are logged, not written into master CSV.
[ ] USB cable and power are stable.

25.5 MQTT messages missing
[ ] Broker running.
[ ] Correct host/IP.
[ ] Same network.
[ ] Firewall not blocking.
[ ] Topic names match.
[ ] Client IDs unique.
[ ] Wi-Fi reconnect logic exists.
[ ] Messages include device ID and sequence number.

26. Preferred Project Folder Structures
26.1 Raspberry Pi Python logger
project_name/
├── README_START_HERE.md
├── RUN_INSTRUCTIONS.md
├── TEST_INSTRUCTIONS.md
├── main.py
├── config/
│   ├── settings.json
│   ├── device_map.json
│   └── channel_map.json
├── src/
│   ├── acquisition.py
│   ├── serial_devices.py
│   ├── mqtt_client.py
│   ├── storage.py
│   ├── plotting.py
│   └── diagnostics.py
├── tools/
│   ├── embedded_link_diagnostic.py
│   └── serial_port_scan.py
├── runtime_data/
│   ├── logs/
│   ├── data/
│   └── diagnostics/
└── docs/

26.2 Arduino project
arduino_sensor_node/
├── README.md
├── arduino_sensor_node.ino
├── protocol.md
├── wiring.md
├── libraries.txt
└── test_messages.txt

26.3 PlatformIO ESP32 project
esp32_sensor_node/
├── platformio.ini
├── src/
│   └── main.cpp
├── include/
│   └── config.h
├── lib/
├── test/
├── protocol.md
└── wiring.md

26.4 MicroPython project
micropython_node/
├── README.md
├── main.py
├── boot.py
├── lib/
│   ├── ssd1306.py
│   └── umqtt/
├── upload.sh
├── upload.bat
├── protocol.md
└── wiring.md

27. Standard Documentation Required for Embedded Projects
Every embedded project should include:
README_START_HERE.md
WIRING.md
PROTOCOL.md
LIBRARIES.md
FLASH_UPLOAD_INSTRUCTIONS.md
TEST_INSTRUCTIONS.md
KNOWN_LIMITATIONS.md
DIAGNOSTIC_OUTPUT_EXAMPLE.txt

27.1 WIRING.md minimum fields
Device:
Board:
Power source:
Logic level:
Pin map:
Common ground:
Level shifters:
Sensors:
Outputs:
Known hazards:
Verified date:

27.2 PROTOCOL.md minimum fields
Transport:
Baud rate / topic / endpoint:
Message format:
Required fields:
Example valid message:
Example invalid message:
Error handling:
Sequence number:
Timestamp source:
Units:

27.3 LIBRARIES.md minimum fields
Library:
Side:
    [ ] Computer Python
    [ ] Raspberry Pi Python
    [ ] Arduino C++
    [ ] ESP32 Arduino
    [ ] MicroPython
    [ ] CircuitPython/Blinka
Install method:
Version:
Purpose:
Known compatibility:
Fallback:

28. Core Library Reference
28.1 Computer / Raspberry Pi Python
pyserial
    Serial communication with Arduino, ESP32, Pico, GPS, instruments.

paho-mqtt
    MQTT messaging for distributed sensor networks.

gpiozero
    Friendly Raspberry Pi GPIO.

lgpio
    Lower-level Raspberry Pi GPIO backend.

pigpio
    Advanced GPIO/PWM/servo/remote GPIO.

smbus2
    I2C access from Python.

spidev
    SPI access from Python.

Adafruit-Blinka
    CircuitPython compatibility layer on Raspberry Pi Linux.

numpy
    Arrays, numerical processing, calibration math.

matplotlib
    Plotting and graph export.

sqlite3
    Built-in SQLite historian/database.

Flask
    Local web server or simple dashboard.

PyQt5
    Modern desktop/touchscreen GUI.

Tkinter
    Built-in lightweight GUI.

psutil
    System diagnostics.

pyzmq
    Frontend/backend process messaging.

requests
    HTTP client.

esptool
    ESP32 firmware flashing.

mpremote
    MicroPython file copy, REPL, run support.

28.2 Arduino / ESP32 C++
ArduinoJson
    JSON messages.

PubSubClient
    MQTT client.

WiFi
    ESP32 Wi-Fi.

HTTPClient
    ESP32 HTTP client.

WebServer
    Simple ESP32 web server.

Wire
    I2C.

SPI
    SPI.

Adafruit Unified Sensor
    Base dependency for many Adafruit sensors.

Adafruit BME280 Library
    Temperature/humidity/pressure.

Adafruit ADS1X15
    External ADCs.

DHT sensor library
    DHT temperature/humidity sensors.

OneWire
    OneWire bus.

DallasTemperature
    DS18B20 sensors.

Adafruit INA219
    Current/voltage/power.

Adafruit GFX
    Graphics base.

Adafruit SSD1306
    OLED displays.

U8g2
    Display library.

TFT_eSPI
    TFT display library.

AccelStepper
    Stepper motors.

ESP32Servo
    Servo control on ESP32.

PID_v1
    PID control.

Preferences
    ESP32 persistent key/value storage.

SD
    SD card.

LittleFS / SPIFFS
    Flash filesystem.

28.3 MicroPython
machine
    GPIO, ADC, PWM, I2C, SPI, UART.

time
    Delays and timing.

network
    Wi-Fi.

socket
    TCP/UDP.

ujson
    JSON.

urequests
    HTTP.

umqtt.simple
    MQTT.

neopixel
    WS2812 LEDs.

dht
    DHT sensors.

ssd1306
    OLED display.

onewire
    OneWire bus.

ds18x20
    DS18B20 temperature.

os
    Device filesystem.

sys
    Runtime info.

28.4 CircuitPython / Blinka
board
    Board pin names.

busio
    I2C/SPI/UART objects.

digitalio
    GPIO.

analogio
    Analog input on supported boards.

pwmio
    PWM outputs.

storage
    Filesystem/storage behavior.

adafruit_bme280
    BME280 sensor.

adafruit_ads1x15
    ADS1015/ADS1115 ADCs.

adafruit_ina219
    Current sensor.

adafruit_ssd1306
    OLED display.

adafruit_mcp230xx
    I/O expander.

neopixel
    NeoPixel LEDs.

29. Best-Practice Rules We Should Carry Forward
RULE-EMB-001
Start with a minimal known-good blink or serial test.

RULE-EMB-002
Do not build the full project until board upload and serial monitor work.

RULE-EMB-003
Do not trust USB power alone for motors, heaters, relays, or heavy loads.

RULE-EMB-004
Document wiring before debugging software.

RULE-EMB-005
Use structured serial/MQTT messages.

RULE-EMB-006
Every message should include device ID and sequence number.

RULE-EMB-007
Computer-side Python must validate packets before writing CSV/SQLite.

RULE-EMB-008
Use heartbeat messages for distributed nodes.

RULE-EMB-009
Treat disconnect/reconnect as normal behavior.

RULE-EMB-010
Separate raw device channel names from logical signal names.

RULE-EMB-011
Use simulation mode where possible.

RULE-EMB-012
Keep GUI updates off worker threads.

RULE-EMB-013
Never use 5 V logic directly into 3.3 V-only pins.

RULE-EMB-014
Use apt/system packages on Raspberry Pi for hardware-tied dependencies when practical.

RULE-EMB-015
Do not assume Arduino libraries install with pip; Arduino libraries belong in Arduino IDE/CLI/PlatformIO.

RULE-EMB-016
Do not assume MicroPython can use normal desktop Python packages.

RULE-EMB-017
Pin library versions once a hardware project works.

RULE-EMB-018
Record board core version, library versions, and firmware version.

RULE-EMB-019
Keep a known-good diagnostic sketch/script for every hardware setup.

RULE-EMB-020
Preserve data first; polish UI second.

30. Definition of Done for Embedded Setup
An embedded/Raspberry Pi/Arduino/ESP32 project setup is acceptable when:
[ ] Target device type identified.
[ ] Target OS/runtime identified.
[ ] Board model identified.
[ ] Upload method verified.
[ ] Serial port verified.
[ ] Correct drivers installed.
[ ] Correct board package/core installed.
[ ] Required libraries listed.
[ ] Library install method documented.
[ ] Minimal blink test passes.
[ ] Minimal serial test passes.
[ ] Wiring documented.
[ ] Logic levels checked.
[ ] Data protocol documented.
[ ] Diagnostic script exists.
[ ] Failure modes documented.
[ ] Offline install notes included if needed.
[ ] Known-good versions recorded.

Core rule:
Do not treat embedded setup as incidental.

For these projects, the setup is part of the engineering system.

DAQ and Safety
