---
document_id: DOC-260
title: "I2C Communication Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-260
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# I2C Communication Guide

260_I2C_COMMUNICATION_GUIDE
0. Purpose
This document explains I2C communication and how we typically use it in Raspberry Pi, Arduino, ESP32, Pico, LabJack-adjacent, sensor, display, and DAQ-style projects.
It covers:
what I2C is
how I2C wiring works
when to use I2C
when not to use I2C
Raspberry Pi I2C setup
Arduino / ESP32 I2C setup
MicroPython I2C setup
common sensor/display patterns
address scanning
pull-up resistors
voltage-level issues
common coding examples
common failure modes
diagnostic procedures

The goal is to make I2C less mysterious and to establish a repeatable setup/debugging pattern.

1. What I2C Is
I2C, often written as I²C, is a two-wire digital communication bus.
It is commonly used for short-distance communication between a controller and small peripheral devices.
Typical I2C devices include:
temperature sensors
humidity sensors
pressure sensors
ADCs
DACs
OLED displays
I/O expanders
RTC clock modules
current sensors
EEPROM chips
small sensor breakout boards

I2C usually uses two signal wires:
SDA = serial data
SCL = serial clock

Plus:
GND = common ground
VCC = device power

A basic I2C connection looks like this:
Controller SDA ───────── SDA peripheral
Controller SCL ───────── SCL peripheral
Controller GND ───────── GND peripheral
Controller 3.3V/5V ───── VCC peripheral, if appropriate

2. Why I2C Is Useful
I2C is useful because many devices can share the same two signal wires.
Instead of needing separate signal wires for every sensor, several devices can sit on the same bus:
Raspberry Pi SDA/SCL
        ├── BME280 temperature/pressure/humidity sensor
        ├── ADS1115 external ADC
        ├── SSD1306 OLED display
        └── MCP23017 I/O expander

Each device has an address.
The controller talks to the device by address.
This makes I2C compact and convenient for sensor-heavy projects.

3. Core Concepts
3.1 Controller and Peripheral
Older documents often use “master” and “slave.” Modern language is usually:
controller
peripheral

The controller starts communication.
The peripheral responds.
Typical controllers:
Raspberry Pi
Arduino
ESP32
Raspberry Pi Pico
LabJack, in some supported workflows

Typical peripherals:
sensor breakout board
ADC module
OLED display
RTC module
I/O expander

3.2 I2C Address
Each I2C peripheral has an address.
Common examples:
0x3C    SSD1306 OLED display
0x48    ADS1115 ADC, common default
0x76    BME280/BMP280 sensor, common default
0x77    BME280/BMP280 alternate address
0x68    DS3231 RTC, MPU6050 IMU, common defaults
0x40    INA219 current sensor, common default
0x20    MCP23017 I/O expander, common default

Important:
Two devices on the same bus cannot have the same address unless special handling is used.

Some boards let you change the address with:
solder jumper
address pin
DIP switch
software configuration

3.3 Pull-Up Resistors
I2C lines are open-drain/open-collector style.
That means devices pull the line low, but the line needs resistors to pull it high.
These are called pull-up resistors.
Most breakout boards already include pull-ups.
Common values:
4.7 kΩ
10 kΩ
2.2 kΩ for stronger/faster/noisier buses

Too few pull-ups:
bus may not work
lines float
scanner finds nothing

Too many pull-ups in parallel:
pull-up resistance becomes too low
devices may have trouble pulling lines low
bus current increases

Practical rule:
For a few breakout boards on a short bus, built-in pull-ups usually work.
For long cables, many devices, or unreliable communication, inspect pull-ups deliberately.

3.4 Bus Speed
Common I2C speeds:
100 kHz    standard mode
400 kHz    fast mode
1 MHz      fast mode plus, if supported

For our projects, start with:
100 kHz or 400 kHz

Use slower speed when:
wires are long
signals are noisy
devices are unreliable
level shifting is involved
older devices are used

3.5 Wiring Distance
I2C is meant for short distances on a board or within a small device enclosure.
It is not ideal for long cable runs.
Use I2C for:
sensor board mounted near controller
small display near controller
ADC in same enclosure
I/O expander on same board or nearby harness

Do not use I2C as the first choice for:
long-distance room-to-room wiring
distributed garage sensor networks
electrically noisy cable runs
industrial field wiring
long outdoor cables

For long distances, prefer:
RS-485
CAN
Ethernet
USB with proper device
MQTT over Wi-Fi/Ethernet
serial with robust framing

4. How We Use I2C in Our Applications
We usually use I2C in these patterns.
4.1 Raspberry Pi as the main controller
I2C sensor/display/ADC
        ↓
Raspberry Pi
        ↓
Python logger / GUI / SQLite / graph

Common uses:
temperature sensors
humidity sensors
pressure sensors
ADS1115 ADC modules
OLED status displays
RTC modules
I/O expanders

4.2 Arduino or ESP32 reads sensors, then sends data to computer
I2C sensor
    ↓
Arduino / ESP32
    ↓
USB serial / MQTT / Wi-Fi
    ↓
Raspberry Pi or PC
    ↓
Python logger

Use this when the sensor is physically closer to the microcontroller than to the main computer.
4.3 Raspberry Pi + external ADC
A Raspberry Pi does not have normal built-in analog inputs.
So, to read analog voltages with a Raspberry Pi, we often add an I2C ADC such as:
ADS1115
ADS1015
MCP342x

Pattern:
analog sensor voltage
    ↓
I2C ADC
    ↓
Raspberry Pi I2C
    ↓
Python

4.4 I2C display as a local status panel
Common display:
SSD1306 OLED

Use for:
IP address
sensor status
current reading
error state
logging status
device heartbeat

4.5 I/O expansion
I2C I/O expanders such as MCP23017 can add more digital inputs/outputs.
Pattern:
Raspberry Pi I2C
    ↓
MCP23017
    ↓
buttons / LEDs / relays through driver circuits

Use this when GPIO count is limited.

5. I2C vs UART vs SPI
5.1 I2C
Use I2C when:
many small devices share the same short bus
device has a fixed register map
sensor/display/ADC module already supports I2C
wiring should be compact

5.2 UART / Serial
Use UART/serial when:
communicating between two intelligent devices
Arduino sends structured data to Raspberry Pi
ESP32 sends JSON lines to PC
longer or simpler point-to-point communication is needed

5.3 SPI
Use SPI when:
higher speed is needed
display or ADC requires SPI
full-duplex communication matters
device has chip-select line

SPI uses more wires but is often faster and simpler electrically.

6. Voltage-Level Rules
This is critical.
Common logic levels:
Raspberry Pi GPIO/I2C:
    3.3 V only, not 5 V tolerant.

ESP32:
    3.3 V logic, not 5 V tolerant.

Raspberry Pi Pico:
    3.3 V logic, not 5 V tolerant.

Arduino Uno/Nano classic:
    usually 5 V logic.

Many sensor breakout boards:
    3.3 V or 5 V depending on regulator/level shifter.

Rules:
Never connect 5 V I2C pull-ups to Raspberry Pi SDA/SCL.
Never connect 5 V I2C pull-ups to ESP32 SDA/SCL.
Never assume a breakout is safe just because it has VIN labeled 5V.
Check whether SDA/SCL are pulled up to 5 V or 3.3 V.
Use a level shifter when mixing 5 V and 3.3 V devices.

Safe general approach:
Use 3.3 V I2C bus when Raspberry Pi, ESP32, or Pico is involved.
Power compatible sensor boards from 3.3 V when possible.
Use level shifting for true 5 V I2C devices.

7. Basic Wiring
7.1 Raspberry Pi I2C wiring
Typical Raspberry Pi I2C bus 1 pins:
GPIO2  = SDA
GPIO3  = SCL
GND    = ground
3.3 V  = power for 3.3 V-compatible device

Common physical header pins:
Pin 3  = SDA / GPIO2
Pin 5  = SCL / GPIO3
Pin 6  = GND
Pin 1  = 3.3 V

Wiring:
Pi SDA → sensor SDA
Pi SCL → sensor SCL
Pi GND → sensor GND
Pi 3.3V → sensor VIN/VCC, only if sensor supports 3.3 V

7.2 Arduino Uno I2C wiring
Arduino Uno:
A4 = SDA
A5 = SCL
GND = ground
5V or 3.3V = power depending on module

Many newer Arduino boards also label dedicated SDA/SCL pins.
7.3 ESP32 I2C wiring
ESP32 I2C pins are flexible in software.
Common default:
GPIO21 = SDA
GPIO22 = SCL

But many ESP32 boards allow different pins.
Example:
Wire.begin(21, 22);

7.4 Raspberry Pi Pico I2C wiring
Pico has multiple I2C-capable pin options.
Example MicroPython setup:
i2c = I2C(0, scl=Pin(1), sda=Pin(0))

The exact pins must match the code.

8. Raspberry Pi Setup
8.1 Enable I2C
Run:
sudo raspi-config

Then:
Interface Options
    I2C
        Enable

Reboot if prompted.
8.2 Install tools
sudo apt update
sudo apt install -y i2c-tools python3-smbus

Optional Python library:
python3 -m pip install smbus2

8.3 Scan I2C bus
i2cdetect -y 1

Expected output example:
    0 1 2 3 4 5 6 7 8 9 a b c d e f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --

This means devices were found at:
0x3C
0x48

If nothing appears:
check wiring
check power
check ground
check I2C enabled
check voltage level
check pull-ups
check bus number

9. Raspberry Pi Python I2C Scanner with smbus2
Save as:
tools/i2c_scan_smbus2.py

import sys

try:
    from smbus2 import SMBus
except ImportError:
    print("Missing smbus2. Install with:")
    print("python3 -m pip install smbus2")
    sys.exit(1)

def scan_i2c_bus(bus_number=1):
    found = []

    with SMBus(bus_number) as bus:
        for address in range(0x03, 0x78):
            try:
                bus.write_quick(address)
                found.append(address)
            except OSError:
                pass

    return found

def main():
    bus_number = 1
    found = scan_i2c_bus(bus_number)

    print("I2C scan on bus %d" % bus_number)
    print("=" * 40)

    if not found:
        print("No I2C devices found.")
    else:
        for address in found:
            print("Found device at 0x%02X" % address)

if __name__ == "__main__":
    main()

Run:
python3 tools/i2c_scan_smbus2.py

10. Raspberry Pi Read/Write Register Example
Many I2C devices use registers.
Pattern:
write register address
read register value

Example using smbus2:
from smbus2 import SMBus

BUS_NUMBER = 1
DEVICE_ADDRESS = 0x48
REGISTER = 0x00

with SMBus(BUS_NUMBER) as bus:
    value = bus.read_byte_data(DEVICE_ADDRESS, REGISTER)
    print("Register 0x%02X = 0x%02X" % (REGISTER, value))

Write one byte to a register:
from smbus2 import SMBus

BUS_NUMBER = 1
DEVICE_ADDRESS = 0x48
REGISTER = 0x01
VALUE = 0x83

with SMBus(BUS_NUMBER) as bus:
    bus.write_byte_data(DEVICE_ADDRESS, REGISTER, VALUE)
    print("Wrote 0x%02X to register 0x%02X" % (VALUE, REGISTER))

Important:
Do not write random values to unknown registers.
Read the device datasheet or use a known library.

11. Raspberry Pi with Adafruit Blinka / CircuitPython Libraries
For many sensors, it is easier to use a library than manually read registers.
Install Blinka:
python3 -m pip install Adafruit-Blinka

Example BME280 install:
python3 -m pip install adafruit-circuitpython-bme280

Example code:
import time
import board
import busio
import adafruit_bme280.basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)

while True:
    print("Temperature: %.2f C" % sensor.temperature)
    print("Humidity: %.2f %%" % sensor.humidity)
    print("Pressure: %.2f hPa" % sensor.pressure)
    print()
    time.sleep(1.0)

Use Blinka/CircuitPython libraries when:
the sensor has a mature Adafruit library
you want faster development
you do not need to manually study the register map

Use lower-level smbus2 when:
you are writing a custom driver
you need exact register control
the device has no high-level library
you need minimal dependencies

12. Arduino I2C Scanner
Use this first on Arduino/ESP32 when testing I2C wiring.
#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }

  Serial.println("I2C Scanner");
}

void loop() {
  byte error;
  byte address;
  int count = 0;

  Serial.println("Scanning...");

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Found I2C device at 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
      count++;
    }
  }

  if (count == 0) {
    Serial.println("No I2C devices found.");
  } else {
    Serial.print("Found ");
    Serial.print(count);
    Serial.println(" device(s).");
  }

  Serial.println();
  delay(3000);
}

Arduino Uno wiring:
A4 → SDA
A5 → SCL
GND → GND
VCC → sensor power

13. ESP32 I2C Scanner
ESP32 often uses custom SDA/SCL pins.
Common default:
SDA = GPIO21
SCL = GPIO22

Scanner:
#include <Wire.h>

const int SDA_PIN = 21;
const int SCL_PIN = 22;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(SDA_PIN, SCL_PIN);

  Serial.println("ESP32 I2C Scanner");
}

void loop() {
  byte error;
  byte address;
  int count = 0;

  Serial.println("Scanning...");

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Found I2C device at 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
      count++;
    }
  }

  if (count == 0) {
    Serial.println("No I2C devices found.");
  }

  Serial.println();
  delay(3000);
}

If scan fails:
confirm pins match code
confirm board pin labels
confirm sensor is powered
confirm ground is shared
confirm pull-ups go to 3.3 V, not 5 V

14. Arduino Register Read Example
#include <Wire.h>

const byte DEVICE_ADDRESS = 0x48;
const byte REGISTER_ADDRESS = 0x00;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  Serial.println("I2C register read example");
}

void loop() {
  Wire.beginTransmission(DEVICE_ADDRESS);
  Wire.write(REGISTER_ADDRESS);
  byte error = Wire.endTransmission(false);

  if (error != 0) {
    Serial.print("Write/register select failed, error ");
    Serial.println(error);
    delay(1000);
    return;
  }

  Wire.requestFrom(DEVICE_ADDRESS, (byte)1);

  if (Wire.available()) {
    byte value = Wire.read();
    Serial.print("Register value: 0x");
    if (value < 16) {
      Serial.print("0");
    }
    Serial.println(value, HEX);
  } else {
    Serial.println("No data received.");
  }

  delay(1000);
}

This pattern is common:
begin transmission
write register address
end transmission, often with repeated start
request bytes
read bytes

15. MicroPython I2C Scanner
For ESP32 or Pico running MicroPython:
from machine import Pin, I2C
import time

# Example for ESP32 common pins:
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# Example for Pico might be:
# i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

while True:
    devices = i2c.scan()

    if devices:
        print("Found I2C devices:")
        for address in devices:
            print("  0x%02X" % address)
    else:
        print("No I2C devices found.")

    time.sleep(3)

If using Pico, confirm the chosen pins support the selected I2C peripheral.

16. MicroPython Register Read/Write
Read one byte from a register:
from machine import Pin, I2C

ADDRESS = 0x48
REGISTER = 0x00

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

data = i2c.readfrom_mem(ADDRESS, REGISTER, 1)
print(data[0])

Write one byte to a register:
from machine import Pin, I2C

ADDRESS = 0x48
REGISTER = 0x01
VALUE = 0x83

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

i2c.writeto_mem(ADDRESS, REGISTER, bytes([VALUE]))

17. CircuitPython / Blinka I2C Scanner
import board
import busio
import time

i2c = busio.I2C(board.SCL, board.SDA)

while not i2c.try_lock():
    pass

try:
    while True:
        devices = i2c.scan()
        print("I2C addresses found:", ["0x%02X" % x for x in devices])
        time.sleep(2)
finally:
    i2c.unlock()

This is useful on:
Raspberry Pi with Blinka
CircuitPython boards
some supported single-board computers

18. Common Device Examples
18.1 ADS1115 external ADC
Use when:
Raspberry Pi needs analog input
higher-resolution analog measurement is needed
slow precision measurement is acceptable

Typical address:
0x48

Adafruit install:
python3 -m pip install adafruit-circuitpython-ads1x15

Example:
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

chan = AnalogIn(ads, ADS.P0)

while True:
    print("Raw:", chan.value, "Voltage:", chan.voltage)
    time.sleep(1.0)

18.2 SSD1306 OLED
Use for:
small local status display
IP address
sensor values
error state

Typical address:
0x3C

18.3 BME280 / BMP280
Use for:
temperature
humidity, BME280 only
pressure
environment monitoring

Typical addresses:
0x76
0x77

18.4 INA219
Use for:
voltage
current
power
small power monitoring

Typical address:
0x40

18.5 MCP23017 I/O expander
Use for:
extra digital inputs
extra digital outputs
buttons
LEDs
relay-driver inputs, through proper circuitry

Typical address:
0x20

19. Address Conflicts
Problem:
Two devices have the same I2C address.

Symptoms:
scanner shows only one address
one or both devices behave strangely
reads return nonsense
library cannot initialize

Fixes:
change address jumper
change address pin wiring
use a different version of the sensor board
use an I2C multiplexer such as TCA9548A
use a second I2C bus if controller supports it

I2C multiplexer pattern:
controller I2C
    ↓
TCA9548A multiplexer
    ├── channel 0 → device at 0x76
    ├── channel 1 → another device also at 0x76
    └── channel 2 → another device also at 0x76

20. Common Failure Modes
20.1 Scanner finds nothing
Check:
SDA/SCL swapped
no common ground
device not powered
wrong voltage
I2C not enabled
wrong bus number
bad cable
bad breadboard connection
missing pull-ups
device damaged
wrong pins in code

20.2 Scanner finds address but library fails
Check:
wrong device library
wrong address in code
device variant differs from expected chip
library expects different register ID
sensor board clone uses different chip
bus speed too high
power unstable

20.3 Works sometimes, fails sometimes
Check:
long wires
weak/too-strong pull-ups
loose jumper wires
electrical noise
shared power sag
bus speed too high
multiple devices with pull-ups causing wrong effective resistance

20.4 Raspberry Pi locks up or gives remote I/O error
Common causes:
device not responding
wiring problem
wrong voltage
bus contention
pull-up issue
driver/library error

Try:
disconnect devices
connect one device at a time
run i2cdetect
lower bus speed
use shorter wires
verify 3.3 V pull-ups

20.5 Address appears as UU in i2cdetect
This means the address is already claimed by a kernel driver.
Do not necessarily treat this as a failure.
It means Linux has a driver bound to that address.

21. Diagnostic Procedure
Use this order every time.
1. Identify controller board.
2. Identify peripheral device.
3. Confirm voltage compatibility.
4. Confirm power wiring.
5. Confirm common ground.
6. Confirm SDA/SCL pins.
7. Confirm pull-ups.
8. Enable I2C if needed.
9. Run bus scanner.
10. Confirm expected address.
11. Run manufacturer/library example.
12. Only then integrate into project code.

Do not debug a full DAQ program before the scanner works.

22. Standard I2C Install Record
I2C INSTALL / SETUP RECORD

Project:
Date:
Controller:
Operating system:
Language/runtime:
I2C bus number:
SDA pin:
SCL pin:
Bus voltage:
Bus speed:
Pull-up resistors:
Level shifter used? Yes/No:

Devices:
    Device name:
    Chip:
    Expected address:
    Detected address:
    Library used:
    Power voltage:
    Notes:

Scanner result:
Library test result:
Known issues:

23. Standard Python I2C Diagnostic Report
Save as:
tools/i2c_diagnostic_report.py

import os
import sys
import time
import traceback

REPORT_DIR = "diagnostics"

def safe_makedirs(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)

def check_import(module_name):
    try:
        __import__(module_name)
        return "PASS"
    except Exception as exc:
        return "FAIL: %r" % exc

def scan_with_smbus2(bus_number=1):
    from smbus2 import SMBus

    found = []

    with SMBus(bus_number) as bus:
        for address in range(0x03, 0x78):
            try:
                bus.write_quick(address)
                found.append(address)
            except OSError:
                pass

    return found

def main():
    safe_makedirs(REPORT_DIR)

    lines = []
    lines.append("I2C DIAGNOSTIC REPORT")
    lines.append("=" * 72)
    lines.append("timestamp: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("python: %s" % sys.version)
    lines.append("cwd: %s" % os.getcwd())
    lines.append("")

    lines.append("IMPORT CHECKS")
    lines.append("-" * 72)
    for module in ["smbus2", "board", "busio"]:
        lines.append("%s: %s" % (module, check_import(module)))

    lines.append("")

    lines.append("SMBUS2 BUS SCAN")
    lines.append("-" * 72)

    try:
        found = scan_with_smbus2(bus_number=1)

        if found:
            for address in found:
                lines.append("FOUND: 0x%02X" % address)
        else:
            lines.append("No devices found on bus 1.")

    except Exception:
        lines.append("smbus2 scan failed:")
        lines.append(traceback.format_exc())

    path = os.path.join(REPORT_DIR, "i2c_diagnostic_report.txt")

    with open(path, "w") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))
    print("")
    print("Wrote:", path)

if __name__ == "__main__":
    main()

Run:
python3 tools/i2c_diagnostic_report.py

24. How I2C Fits Into Our DAQ Architecture
For a serious DAQ/logger/control project, do not bury I2C reads directly in GUI code.
Better structure:
I2C device adapter
    ↓
acquisition thread
    ↓
telemetry queue
    ↓
writer queue
    ↓
CSV / SQLite
    ↓
GUI graph/status panel

Example adapter shape:
class I2CSensorAdapter(object):
    def connect(self):
        raise NotImplementedError

    def read_telemetry(self):
        raise NotImplementedError

    def diagnostics(self):
        raise NotImplementedError

Example concrete adapter:
class SimulatedI2CSensorAdapter(object):
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        return True

    def read_telemetry(self):
        return {
            "temperature_c": 23.4,
            "humidity_pct": 45.0,
            "quality": "SIMULATED",
        }

    def diagnostics(self):
        return {
            "adapter": "SimulatedI2CSensorAdapter",
            "connected": self.connected,
        }

Then a real BME280 adapter can replace it later.
Rule:
The GUI should not care whether the sensor is I2C, serial, MQTT, simulated, or LabJack.
The acquisition layer should translate device-specific details into named telemetry.

25. Example: I2C Sensor Adapter Pattern
import time

class BME280Adapter(object):
    def __init__(self):
        self.sensor = None
        self.last_error = ""

    def connect(self):
        try:
            import board
            import busio
            import adafruit_bme280.basic as adafruit_bme280

            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
            return True

        except Exception as exc:
            self.last_error = repr(exc)
            self.sensor = None
            return False

    def is_connected(self):
        return self.sensor is not None

    def read_telemetry(self):
        if self.sensor is None:
            raise RuntimeError("BME280 sensor is not connected")

        return {
            "timestamp": time.time(),
            "temperature_c": float(self.sensor.temperature),
            "humidity_pct": float(self.sensor.humidity),
            "pressure_hpa": float(self.sensor.pressure),
            "quality": "GOOD",
        }

    def diagnostics(self):
        return {
            "adapter": "BME280Adapter",
            "connected": self.is_connected(),
            "last_error": self.last_error,
        }

Use this kind of structure for formal projects.
For quick experiments, a simple script is fine.

26. Acceptance Tests
An I2C setup is ready when:
[ ] Controller board identified.
[ ] Peripheral device identified.
[ ] Voltage levels checked.
[ ] SDA/SCL wiring checked.
[ ] Common ground connected.
[ ] Pull-ups understood.
[ ] I2C enabled if using Raspberry Pi.
[ ] Bus scanner detects expected address.
[ ] Device library example runs.
[ ] Readings make physical sense.
[ ] Diagnostic script produces output.
[ ] Project records address, bus, library, and wiring.

For serious projects:
[ ] I2C reads are isolated in an adapter.
[ ] Bad reads are logged with quality flags.
[ ] Acquisition continues or fails gracefully if device disconnects.
[ ] Raw values and converted values are distinguishable.
[ ] Configuration records address and bus number.
[ ] The system can run in simulated mode.

27. Common Rules
RULE-I2C-001
Always run a bus scanner before debugging application code.

RULE-I2C-002
Never connect 5 V pull-ups to 3.3 V-only controllers.

RULE-I2C-003
Use short wires first.

RULE-I2C-004
Add one device at a time.

RULE-I2C-005
Record every detected address.

RULE-I2C-006
Do not write random register values to unknown devices.

RULE-I2C-007
Use high-level libraries for common sensors unless low-level control is needed.

RULE-I2C-008
Use named telemetry variables in serious DAQ code.

RULE-I2C-009
Treat missing devices as expected faults, not impossible errors.

RULE-I2C-010
Do not let I2C hardware details leak into GUI code.

28. Closing Principle
I2C is best treated as a compact local sensor/control bus.
The standard workflow is:
wire one device
verify voltage
scan the bus
confirm address
run the simplest library example
wrap it in a device adapter
log named telemetry
add diagnostics
then integrate into the larger system

For our projects, I2C is usually not the whole system.
It is one hardware communication layer feeding a larger Python architecture:
sensor or peripheral
    → I2C
        → Raspberry Pi / Arduino / ESP32 / Pico
            → Python or firmware layer
                → logging / graphing / control / diagnostics

Python on Android
