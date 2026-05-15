---
document_id: DOC-010
title: "Windows Software Download and Installation Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-010
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Windows Software Download and Installation Guide

230_WINDOWS_SOFTWARE_DOWNLOAD_AND_INSTALLATION_GUIDE
0. Purpose
This guide explains how to download, install, and verify the major Windows programs, drivers, runtimes, and vendor tools commonly needed for Python, Raspberry Pi, Arduino, ESP32, Visual Basic/.NET, laboratory instruments, serial devices, LabJack devices, and hardware-control projects.
This guide focuses on software that is not installed only through pip.
Pip is used for Python libraries. This document is mainly for programs, IDEs, drivers, runtimes, board managers, and vendor tools that must be downloaded and installed separately.
Examples include:
Python installer
Visual Studio Code
Visual Studio Community
Git
7-Zip
Raspberry Pi Imager
Arduino IDE
Arduino CLI
Thonny
NI-VISA
LabJack UD driver
LabJack LJM driver
LabJackPython
USB serial drivers
PuTTY
Node.js

Core rule:
Download from the official source.
Install one tool at a time.
Verify each tool before moving on.
Record what worked.

Installation is not complete just because the installer finished. Installation is complete when the tool can be verified from the command line, from its utility program, or with attached hardware where applicable.

1. Installation Order
For a typical Windows engineering/programming workstation, install in this order:
1. 7-Zip
2. Python
3. Git
4. Visual Studio Code
5. Visual Studio Community, if using Visual Basic / C# / .NET
6. Raspberry Pi Imager
7. Arduino IDE
8. Arduino CLI, optional
9. Thonny, especially for MicroPython / Pico work
10. NI-VISA, if controlling lab instruments through VISA
11. PyVISA through pip, after NI-VISA or another VISA backend
12. LabJack software/drivers, if using LabJack devices
13. USB serial drivers, only if Windows does not detect the board/device
14. PuTTY or SSH tool, if remote terminal access is needed
15. Node.js, only if a project requires JavaScript/npm tooling

Do not install everything blindly. Install only what the project needs.

2. General Download Safety
Use official sources whenever possible.
Before running an installer, check:
[ ] Did it come from the official vendor/project?
[ ] Is it the correct operating system?
[ ] Is it 64-bit or 32-bit as needed?
[ ] Is it the installer, not source code?
[ ] Is this machine allowed to install software?
[ ] Do I need administrator rights?
[ ] Is this installer actually required for this project?

Avoid:
random driver bundle sites
fake download buttons
ad-heavy mirror sites
unknown repackaged installers
download managers
"one-click driver updater" utilities

When in doubt, stop and verify the official source.

3. 7-Zip
What it is
7-Zip is a file archiver used to open and create compressed files such as:
.zip
.7z
.tar.gz
.tar.bz2

It is often needed because GitHub/source packages and offline installers may come as compressed archives.
Install
Download the Windows installer from the official 7-Zip website.
For most modern Windows computers, choose:
64-bit Windows x64 .exe installer

Use 32-bit only if the target machine is 32-bit Windows.
Verify
Right-click a .zip or .7z file and confirm that a 7-Zip menu appears.
You can also open 7-Zip File Manager from the Start menu.

4. Python
What it is
Python is the main programming language used for automation, simulations, DAQ tools, plotting, file processing, hardware communication, and prototype GUIs.
Install
Download Python from the official Python website.
During installation, enable:
Add python.exe to PATH

This is one of the most important installer options. If Python is not added to PATH, Windows may not recognize the python command.
Verify
Open Command Prompt or PowerShell:
python --version

Then:
python -m pip --version

Also try:
py --version

Correct pip usage
Use:
python -m pip install package_name

instead of only:
pip install package_name

This ensures pip belongs to the Python interpreter you are actually using.
Upgrade pip, modern systems only
On a modern Python installation:
python -m pip install --upgrade pip

Do not assume this is safe for old/legacy Python installations unless the environment has been checked.

5. Git
What it is
Git is version-control software. It is used to download repositories, track project changes, and work with GitHub projects.
Install
Download Git for Windows from the official Git website.
Accept the default options unless a project has a specific reason to change them.
Verify
git --version

Basic use
Download a repository:
git clone https://github.com/user/project.git

Move into it:
cd project

If Git is not required, downloading a ZIP from GitHub may be simpler.

6. Visual Studio Code
What it is
Visual Studio Code is a lightweight code editor used for Python, Markdown documentation, Git projects, Arduino-adjacent work, and general code editing.
Install
Download VS Code from Microsoft’s official VS Code site.
Recommended installer:
Windows x64 User Installer

Recommended install checkboxes:
Add to PATH
Add "Open with Code" to file context menu
Add "Open with Code" to folder context menu
Register Code as an editor for supported file types

Useful extensions
Install inside VS Code:
Python
Pylance
C/C++
Arduino
Markdown All in One
GitHub Pull Requests and Issues

Verify
Open a folder.
Create:
hello.py

Add:
print("Hello from VS Code")

Run it.

7. Visual Studio Community
What it is
Visual Studio Community is Microsoft’s full IDE for Visual Basic, C#, .NET desktop apps, Windows Forms, WPF, and larger compiled Windows software projects.
Use Visual Studio Community when working on:
Visual Basic
C#
.NET desktop applications
Windows Forms
WPF
large compiled Windows applications

Use VS Code for lighter scripting/editing.
Install
Download Visual Studio Community from Microsoft’s official Visual Studio site.
Run the Visual Studio Installer.
Select the workload:
.NET desktop development

Optional workloads depending on project:
Desktop development with C++
Python development
Node.js development

Do not install unnecessary workloads unless storage space and installation time are not a concern.
Verify
Open Visual Studio and create a new project:
Visual Basic Console App

Run a simple test:
Console.WriteLine("Hello from Visual Basic")

8. Raspberry Pi Imager
What it is
Raspberry Pi Imager writes Raspberry Pi OS or another operating system image to a microSD card.
Install
Download Raspberry Pi Imager from the official Raspberry Pi software page.
Use
1. Insert microSD card.
2. Open Raspberry Pi Imager.
3. Choose Raspberry Pi device.
4. Choose operating system.
5. Choose storage.
6. Configure hostname/Wi-Fi/SSH if needed.
7. Write image.

Warning
Writing the image erases the selected storage device.
Double-check the selected drive before clicking Write.

9. Arduino IDE
What it is
Arduino IDE is the primary graphical program for writing and uploading Arduino sketches to Arduino boards and many ESP32 boards.
Install
Download Arduino IDE from Arduino’s official software page.
Use the current Arduino IDE unless a project specifically requires the older legacy IDE.
Verify
Open Arduino IDE.
Plug in an Arduino.
Select:
Tools → Board
Tools → Port

Open:
File → Examples → 01.Basics → Blink

Upload.
If the onboard LED blinks, the toolchain works.

10. ESP32 Board Support for Arduino IDE
What it is
The ESP32 board package lets Arduino IDE compile and upload code to ESP32 boards.
Install through Arduino IDE
1. Open Arduino IDE.
2. Open Boards Manager.
3. Search "esp32".
4. Install "esp32 by Espressif Systems".
5. Select the correct ESP32 board under Tools → Board.

Common board selections:
ESP32 Dev Module
ESP32-WROOM-DA Module
ESP32-S3 Dev Module
ESP32-C3 Dev Module
Heltec WiFi LoRa 32

If the exact board is unknown, start with the closest generic board and verify upload.
Verify
Open a basic blink sketch.
Select the ESP32 board and COM port.
Upload.
If upload fails:
[ ] Try a known data-capable USB cable.
[ ] Close Serial Monitor.
[ ] Hold BOOT while upload starts.
[ ] Tap EN/RESET if needed.
[ ] Lower upload speed.
[ ] Confirm the board package and board selection.
[ ] Confirm the correct COM port.

11. Arduino CLI
What it is
Arduino CLI is the command-line version of Arduino’s build/upload/library/board-management system.
Use it when:
repeatable build instructions are needed
a package needs scripted tests
a project should build without opening Arduino IDE
version-controlled build commands are preferred

Most users can start with Arduino IDE and add Arduino CLI later.
Install
Download or install Arduino CLI using the official Arduino CLI instructions.
Verify
arduino-cli version

Update indexes:
arduino-cli core update-index
arduino-cli lib update-index

List connected boards:
arduino-cli board list

Install Arduino AVR core:
arduino-cli core install arduino:avr

Install ESP32 core:
arduino-cli core install esp32:esp32

Install a library:
arduino-cli lib install ArduinoJson

Compile an Arduino Uno sketch:
arduino-cli compile --fqbn arduino:avr:uno MySketch

Upload:
arduino-cli upload -p COM5 --fqbn arduino:avr:uno MySketch

12. Thonny
What it is
Thonny is a beginner-friendly Python IDE and is also useful for MicroPython / Raspberry Pi Pico work.
Install
Download Thonny from the official Thonny website.
Verify
Open Thonny and run:
print("Hello from Thonny")

MicroPython / Pico use
For MicroPython/Pico use:
Tools → Options → Interpreter

Select the MicroPython interpreter appropriate for the board.
Use Thonny when:
programming Raspberry Pi Pico
learning Python basics
using MicroPython
wanting a simple editor with a Run button

13. NI-VISA
What it is
NI-VISA is a vendor driver/runtime for communicating with laboratory instruments using VISA.
Use NI-VISA when controlling instruments such as:
programmable power supplies
oscilloscopes
electronic loads
function generators
digital multimeters
GPIB instruments
USB-TMC instruments
Ethernet/LXI instruments
serial instruments

Install
Download NI-VISA from NI’s official download page.
Depending on the current NI installer flow, this may involve NI Package Manager.
Install NI-VISA.
Restart Windows if requested.
Verify with NI MAX
After installing NI-VISA, open:
NI MAX

NI MAX means:
NI Measurement & Automation Explorer

Look for instruments under:
Devices and Interfaces

Common VISA resource formats:
USB0::...
TCPIP0::...
GPIB0::...
ASRL3::INSTR

Bitness rule
Python and the VISA runtime should normally match bitness.
Typical modern setup:
64-bit Windows
64-bit Python
64-bit NI-VISA

Avoid mixing:
32-bit Python with 64-bit NI-VISA
64-bit Python with 32-bit NI-VISA

unless there is a specific reason and the setup is verified.

14. PyVISA
What it is
PyVISA is the Python package used to access VISA instruments from Python code.
PyVISA is installed through pip, but it needs a VISA backend.
Common backends:
NI-VISA
Keysight VISA
Rohde & Schwarz VISA
TekVISA
pyvisa-py

For our typical Windows lab-instrument workflow:
Install NI-VISA first.
Then install PyVISA.
Then verify with pyvisa-info.

Install PyVISA
python -m pip install pyvisa

Optional pure-Python backend:
python -m pip install pyvisa-py

Verify
Run:
pyvisa-info

Then test in Python:
import pyvisa

rm = pyvisa.ResourceManager()
print(rm.list_resources())

Safe first instrument test
For a programmable power supply or other instrument, do not make the first command energize outputs.
Use identity query first:
import pyvisa

rm = pyvisa.ResourceManager()
print(rm.list_resources())

inst = rm.open_resource("YOUR_RESOURCE_STRING_HERE")
print(inst.query("*IDN?"))
inst.close()

Only send output-enable commands after the safe-state policy is defined.

15. LabJack Software and Drivers
What it is
LabJack devices are DAQ units used for analog inputs, digital I/O, counters, timers, and control.
The important distinction is:
U3 / U6 / UE9
    → UD driver on Windows
    → LabJackPython
    → import u3 / import u6 / import ue9

T4 / T7 / T8 / Digit
    → LJM library
    → Python_LJM / labjack-ljm
    → from labjack import ljm

This distinction matters. Do not use LJM as the normal stack for U3/U6/UE9.

16. LabJack U3 / U6 / UE9
Correct stack
For U3, U6, and UE9 on Windows:
LabJack UD driver / UD library
LabJackPython
LJControlPanel / LJLogUD / LJStreamUD utilities

Correct Python imports:
import u3
import u6
import ue9

Use the import matching the device.
Install
Install the LabJack UD software/driver package for U3/U6/UE9 from LabJack’s official support/download area.
Then install LabJackPython if it is not already available in the Python environment:
python -m pip install LabJackPython

For legacy/offline systems, especially Windows XP or old Python environments, use the known-good LabJackPython and UD installer versions for that machine rather than assuming modern pip will work.
Verify with LabJack utility
Open:
LJControlPanel

Confirm that the U3/U6/UE9 appears.
For logging utilities, UD-series tools include:
LJLogUD
LJStreamUD

Use these to sanity-check device communication outside Python.
Verify U6 in Python
try:
    import u6

    d = u6.U6()
    print("Opened U6")
    print(d)
    d.close()
except Exception as exc:
    print("LabJack U6 test failed:", repr(exc))

Verify U3 in Python
try:
    import u3

    d = u3.U3()
    print("Opened U3")
    print(d)
    d.close()
except Exception as exc:
    print("LabJack U3 test failed:", repr(exc))

Notes
For our U6 work, the known import pattern has often been:
import u6

not:
from labjack import u6

Use what works for the installed LabJackPython environment and record it in the project install notes.

17. LabJack T-Series / Digit
Correct stack
For T4, T7, T8, and Digit:
LJM driver/library
Kipling utility
Python_LJM / labjack-ljm

Correct Python import:
from labjack import ljm

Install
Install the LJM software package from LabJack’s official support/download area.
Install Python support if needed:
python -m pip install labjack-ljm

Verify with Kipling
Open:
Kipling

Confirm the device appears and live readings update.
Verify in Python
from labjack import ljm

handle = ljm.openS("ANY", "ANY", "ANY")
print(ljm.getHandleInfo(handle))
ljm.close(handle)

Notes
Do not assume U3/U6 examples apply to T-series devices.
Do not assume T-series LJM examples apply to U3/U6 devices.

18. USB Serial Drivers
What they are
Many Arduino/ESP32 boards appear to Windows as a serial COM port. Some boards need USB-to-serial drivers.
Common USB serial chips:
CP210x
CH340 / CH341
FTDI
native USB

Do not install random driver bundles. Identify the chip or board first.

19. CP210x Driver
What it is
CP210x USB-to-UART chips are common on ESP32 and other development boards.
Install
Download CP210x VCP drivers from Silicon Labs’ official driver page.
Verify
Plug in the board.
Open Device Manager.
Look for:
Silicon Labs CP210x USB to UART Bridge

or a new COM port.

20. CH340 / CH341 Driver
What it is
CH340/CH341 USB-serial chips are common on inexpensive Arduino Nano-compatible boards and some ESP boards.
Install
Download the CH340/CH341 driver from WCH.
Look for:
CH341SER

Verify
Open Device Manager.
Look for:
USB-SERIAL CH340

or a new COM port.

21. FTDI Driver
What it is
FTDI chips are another common USB-to-serial interface.
Install
Download VCP drivers from FTDI’s official driver page.
Verify
Open Device Manager.
Look for:
USB Serial Port (COMx)

22. PuTTY / SSH Tool
What it is
PuTTY is an SSH/telnet client for Windows. It is useful for logging into Raspberry Pis, Linux machines, and network devices.
Modern Windows often has SSH built in, so PuTTY may not be required.
Install PuTTY
Download PuTTY from the official PuTTY site or its official release page.
Verify
Open PuTTY.
Enter a hostname, for example:
raspberrypi.local

Choose:
SSH

Connect.
Built-in Windows SSH
PowerShell may work directly:
ssh username@raspberrypi.local

Example:
ssh pi@raspberrypi.local

Use the actual username configured on the Raspberry Pi.

23. Node.js
What it is
Node.js is a JavaScript runtime. It is only needed when a project uses JavaScript tools such as:
npm
web dashboards
frontend build tools
Electron
some local web tooling

Install
Download the LTS installer from the official Node.js website unless a project specifically requires another version.
Verify
node --version

Then:
npm --version

24. GitHub Desktop
What it is
GitHub Desktop is a graphical tool for working with GitHub repositories.
Install it if a project needs GitHub but the user is not using command-line Git.
If the workflow is command-line based, install Git instead.
Install
Download GitHub Desktop from GitHub’s official desktop site.
Verify
Open GitHub Desktop and sign in.
Clone a test repository or open an existing local repository.

25. Recommended Verification Checklist
After installing the full workstation stack, open Command Prompt or PowerShell and run:
python --version
python -m pip --version
git --version
code --version

If installed:
arduino-cli version
node --version
npm --version
pyvisa-info

Python hardware/import checks:
python -c "import serial; print('pyserial ok')"
python -c "import pyvisa; print('pyvisa ok')"

For LabJack U6:
python -c "import u6; print('u6 import ok')"

For LabJack U3:
python -c "import u3; print('u3 import ok')"

For LabJack LJM / T-series:
python -c "from labjack import ljm; print('ljm import ok')"

If any of these fail, record the exact error text.

26. Standard Install Record
For repeatable projects, record this after installing:
INSTALL-RECORD

Computer:
Windows version:
Administrator rights used? Yes/No:

Python version:
Python path:
pip version:

Git version:
VS Code version:
Visual Studio version:
Arduino IDE version:
Arduino CLI version:
Raspberry Pi Imager version:
Thonny version:

NI-VISA version:
PyVISA version:

LabJack device type:
    [ ] U3
    [ ] U6
    [ ] UE9
    [ ] T4
    [ ] T7
    [ ] T8
    [ ] Digit

LabJack driver stack:
    [ ] UD driver for U3/U6/UE9
    [ ] LJM driver for T-series/Digit

LabJack Python stack:
    [ ] LabJackPython
    [ ] labjack-ljm / Python_LJM

USB serial drivers installed:
    [ ] CP210x
    [ ] CH340/CH341
    [ ] FTDI
    [ ] Other:

Notes:

27. Common Failure Patterns
python is not recognized
Python is not on PATH or the wrong installer option was chosen.
Try:
py --version

If that works, Python is installed but python is not mapped.
Fix:
Re-run Python installer.
Choose Modify.
Enable PATH option if available.

pip is not recognized
Use:
python -m pip --version

If that fails, pip may not be installed for that Python.
pyvisa.errors.VisaIOError
Possible causes:
NI-VISA not installed
wrong VISA backend
instrument not visible in NI MAX
wrong resource string
instrument turned off
USB/LAN/GPIB problem
firewall problem
Python/VISA bitness mismatch

Could not open serial port
Possible causes:
wrong COM port
Serial Monitor already open
driver missing
bad cable
board disconnected
permissions issue
another program owns the port

Arduino upload fails
Check:
board selected
port selected
USB cable
driver
BOOT button for ESP32
Serial Monitor closed
upload speed

import u6 or import u3 fails
Possible causes:
LabJackPython not installed
wrong Python environment
UD driver not installed on Windows
using T-series/LJM instructions by mistake
using the wrong import style

For U3/U6/UE9, check:
UD driver installed
LJControlPanel can see device
LabJackPython installed
correct import: import u3 / import u6 / import ue9

from labjack import ljm fails
Possible causes:
labjack-ljm not installed
LJM driver not installed
wrong Python environment
using U3/U6/UE9 instructions by mistake

For T-series/Digit, check:
LJM installed
Kipling can see device
labjack-ljm installed
correct import: from labjack import ljm

28. Basic Instrument-Control Verification Flow
Use this order for lab instruments:
1. Install NI-VISA or appropriate vendor VISA runtime.
2. Restart if required.
3. Open NI MAX or vendor utility.
4. Confirm the instrument appears.
5. Query instrument identity in the vendor utility if possible.
6. Install PyVISA.
7. Run pyvisa-info.
8. Run a Python list-resources script.
9. Query *IDN?.
10. Only then attempt control commands.

Python resource scan:
import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_resources()

print("Resources:")
for r in resources:
    print(" ", r)

Identity query:
import pyvisa

RESOURCE = "PASTE_RESOURCE_STRING_HERE"

rm = pyvisa.ResourceManager()
inst = rm.open_resource(RESOURCE)
print(inst.query("*IDN?"))
inst.close()

29. Basic Serial-Board Verification Flow
Use this order for Arduino/ESP32 serial devices:
1. Install Arduino IDE.
2. Plug in board.
3. Confirm COM port appears.
4. Install USB serial driver only if needed.
5. Select board.
6. Select port.
7. Upload Blink.
8. Open Serial Monitor.
9. Upload a simple serial print sketch.
10. Read serial from Python using pyserial.

Arduino serial test:
void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println("hello from board");
  delay(1000);
}

Python serial reader:
import serial

PORT = "COM5"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

while True:
    line = ser.readline().decode("utf-8", "replace").strip()
    if line:
        print(line)

30. Basic Raspberry Pi Verification Flow
Use this order for Raspberry Pi setup:
1. Install Raspberry Pi Imager.
2. Write Raspberry Pi OS to microSD.
3. Configure hostname, user, Wi-Fi, and SSH if needed.
4. Boot Pi.
5. Confirm login locally or over SSH.
6. Update apt package lists.
7. Check Python version.
8. Install project dependencies.
9. Run a small diagnostic script.
10. Only then connect sensors/hardware.

Common first commands on the Pi:
python3 --version
python3 -m pip --version
uname -a
cat /etc/os-release

Update:
sudo apt update

Install common tools:
sudo apt install -y python3-pip python3-venv git

31. Basic LabJack Verification Flow
U3 / U6 / UE9
Use this order:
1. Confirm the device is U3, U6, or UE9.
2. Install the LabJack UD driver/software package.
3. Open LJControlPanel.
4. Confirm the device appears.
5. Confirm a basic reading or configuration utility works.
6. Install/check LabJackPython.
7. Run import test: import u3 or import u6.
8. Open the device in Python.
9. Read one simple analog input.
10. Only then build larger DAQ code.

U6 minimal check:
import u6

d = u6.U6()
print(d.getAIN(0))
d.close()

U3 minimal check:
import u3

d = u3.U3()
print(d.getAIN(0))
d.close()

T-Series / Digit
Use this order:
1. Confirm the device is T4, T7, T8, or Digit.
2. Install LJM.
3. Open Kipling.
4. Confirm the device appears.
5. Confirm readings update.
6. Install/check labjack-ljm.
7. Run import test: from labjack import ljm.
8. Open the device in Python.
9. Read one simple name/address.
10. Only then build larger DAQ code.

Minimal LJM check:
from labjack import ljm

handle = ljm.openS("ANY", "ANY", "ANY")
print(ljm.eReadName(handle, "AIN0"))
ljm.close(handle)

32. Offline Install Notes
For offline or restricted machines, create an install bundle on an online machine.
Bundle structure:
offline_install_bundle/
├── installers/
├── drivers/
├── wheels/
├── docs/
├── README_OFFLINE_INSTALL.md
└── INSTALL_RECORD.txt

For Python wheels:
python -m pip download -r requirements.txt -d wheels

On the offline target:
python -m pip install --no-index --find-links=wheels -r requirements.txt

For non-pip installers:
Put the exact installer .exe/.msi in installers/
Put driver installers in drivers/
Include version numbers and source names in README_OFFLINE_INSTALL.md

For LabJack U3/U6/UE9 offline work, include:
UD installer
LabJackPython package or wheel/source
known-good Python version
U3/U6/UE9 verification script

For LabJack T-series/Digit offline work, include:
LJM installer
labjack-ljm package or wheel/source
known-good Python version
T-series/Digit verification script

33. What to Copy Back When Something Fails
Use this diagnostic block:
INSTALL / SETUP FAILURE REPORT

Tool being installed:
Installer filename:
Download source:
Computer:
Windows version:
32-bit or 64-bit:
Administrator rights? Yes/No:

Command run:
Full error message:
Screenshot available? Yes/No:

Python version:
pip version:
Git version:
Arduino IDE version:
NI-VISA version:
PyVISA version:

LabJack model, if relevant:
LabJack driver installed:
LabJack utility can see device? Yes/No:
Python import attempted:
Python import result:

Hardware attached:
COM ports visible:
Device Manager status:

What already worked:
What already failed:

Command outputs to include:
python --version
python -m pip --version
git --version
pyvisa-info

If serial devices are involved, run:
import serial.tools.list_ports

for p in serial.tools.list_ports.comports():
    print(p.device, p.description, p.hwid)

If LabJack U3/U6/UE9 is involved, run:
try:
    import u6
    print("u6 import ok")
except Exception as exc:
    print("u6 import failed:", repr(exc))

try:
    import u3
    print("u3 import ok")
except Exception as exc:
    print("u3 import failed:", repr(exc))

If LabJack T-series/Digit is involved, run:
try:
    from labjack import ljm
    print("ljm import ok")
except Exception as exc:
    print("ljm import failed:", repr(exc))

34. Core Rule
Installation is not complete when the installer finishes.
Installation is complete only when the tool is verified.
Download.
Install.
Restart if required.
Verify from command line.
Verify with hardware utility if applicable.
Record version.
Then proceed.

For LabJack specifically, keep this locked in:
U3 / U6 / UE9
    = UD driver + LabJackPython

T4 / T7 / T8 / Digit
    = LJM driver + labjack-ljm / Python_LJM

That distinction should be treated as a standing rule in all future setup documents.
