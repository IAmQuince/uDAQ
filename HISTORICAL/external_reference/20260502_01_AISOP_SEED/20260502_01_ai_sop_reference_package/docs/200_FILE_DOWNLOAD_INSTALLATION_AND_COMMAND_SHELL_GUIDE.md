---
document_id: DOC-200
title: "File Download, Installation, and Command Shell Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-200
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# File Download, Installation, and Command Shell Guide

## 0. Purpose

This guide explains how to download, transfer, install, and run software packages in the kinds of environments we commonly work with.

It is intended for users who may not be comfortable with:

- GitHub releases;
- source-code ZIP files;
- command prompt;
- PowerShell;
- Python;
- pip;
- wheel files;
- offline installs;
- Windows XP limitations;
- Raspberry Pi/Linux installs;
- Android/Pydroid quirks;
- driver installers;
- Python package compatibility;
- choosing the correct file from a release page.

The goal is to create a repeatable procedure so that installing or testing a package does not depend on memory, guessing, or fragile chat instructions.

---

## 1. Core Rule

Before downloading or installing anything, identify the target environment.

Do not start with:

```text
What file do I click?

Start with:
What machine is this for?
What OS is it running?
What Python version is installed?
Is it 32-bit or 64-bit?
Is it online or offline?
Does it need hardware drivers?
Does it need to run from a flash drive?

A correct download for one machine may be useless on another.

2. Target Environment Checklist
Before installing, fill this out:
TARGET-ENV-001
Machine name:
Operating system:
OS version:
32-bit or 64-bit:
Python version:
Python path:
pip available? Yes/No:
Internet available? Yes/No:
Admin rights available? Yes/No:
Command shell available:
    [ ] Command Prompt
    [ ] PowerShell
    [ ] Git Bash
    [ ] Linux terminal
    [ ] Pydroid terminal
Target hardware:
Required drivers:
Offline transfer method:
Known constraints:

Examples:
Windows XP legacy machine:
OS: Windows XP Pro SP3, 32-bit
Python: Python(x,y) 2.7.6.1
Internet: No
Shell: Command Prompt
Constraints: no Python 3 syntax, no modern wheels, offline USB transfer

Modern Windows laptop:
OS: Windows 10/11, 64-bit
Python: Python 3.x
Internet: Yes
Shell: PowerShell or Command Prompt
Constraints: likely supports modern pip/wheels

Raspberry Pi:
OS: Raspberry Pi OS
Python: usually python3
Internet: maybe yes/maybe no
Shell: Linux terminal
Constraints: ARM architecture, package wheels may differ from Windows

3. Which Shell Should I Use?
3.1 Windows Command Prompt
Use Command Prompt when:
* instructions show cmd;
* working on Windows XP;
* PowerShell is not installed or behaves oddly;
* you want the most basic Windows shell.
Open it:
Start Menu → Run → cmd

or:
Windows key + R → cmd → Enter

Useful commands:
cd
dir
cd Desktop
cd C:\path\to\folder
python --version
where python

On Windows XP, where may not exist. Use:
echo %PATH%

or search manually for python.exe.

3.2 Windows PowerShell
Use PowerShell when:
* instructions show powershell;
* using modern Windows;
* downloading files with commands;
* running scripts;
* managing batches of files.
Open it:
Start Menu → PowerShell

or right-click a folder and choose:
Open in Terminal

Useful commands:
pwd
ls
cd .\Downloads
python --version
Get-Command python

PowerShell script execution may be blocked. For trusted local scripts, use:
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

For one script only:
powershell -ExecutionPolicy Bypass -File .\script.ps1

Do not run random downloaded scripts unless you understand what they do.

3.3 Linux / Raspberry Pi Terminal
Use terminal for Raspberry Pi/Linux.
Useful commands:
pwd
ls
cd ~/Downloads
python3 --version
which python3
python3 -m pip --version

Package manager:
sudo apt update
sudo apt install package-name

Python package install:
python3 -m pip install package-name

3.4 Pydroid Terminal
Use Pydroid’s built-in terminal for Android Python work.
Important differences:
* Android filesystem paths are different.
* Not every Python package installs.
* GUI behavior is not desktop behavior.
* Kivy/OpenGL issues may need log inspection.
* Some packages need Pydroid plugin packages.
Useful commands:
python --version
pip --version
pwd
ls

4. How to Navigate to the Correct Folder
Most failed command-line installs happen because the user is in the wrong folder.
4.1 Windows Command Prompt
Example:
cd C:\Users\YourName\Downloads\my_package
dir

If the path has spaces:
cd "C:\Users\YourName\Downloads\my package"

4.2 PowerShell
cd "C:\Users\YourName\Downloads\my_package"
ls

4.3 Linux / Raspberry Pi
cd ~/Downloads/my_package
ls

4.4 Confirm You Are in the Right Folder
Look for expected files:
README
setup.py
pyproject.toml
requirements.txt
main.py
tools/
src/

Command:
ls

or on Windows:
dir

5. GitHub Download Guide
GitHub pages can be confusing because there are often several different ways to download something.
There are usually four cases:
1. Download a release asset.
2. Download source code ZIP.
3. Clone the repository with git.
4. Download a single file.

6. GitHub Releases vs Source Code
6.1 Prefer Releases When Available
A GitHub project may have a Releases page.
Use releases when you want:
* installer;
* compiled executable;
* ZIP package;
* wheel file;
* stable version;
* known-good tagged version.
Look for:
Releases
Latest
Assets

Under Assets, you may see files like:
project-1.2.0.zip
project-1.2.0-win64.exe
project-1.2.0-py3-none-any.whl
project-1.2.0.tar.gz
Source code (zip)
Source code (tar.gz)

Important:
Source code (zip)

is not always the same as a ready-to-run package.
It may require building or installing dependencies.

6.2 When to Use “Code → Download ZIP”
Use:
Code → Download ZIP

when:
* there is no formal release;
* you need the current repository files;
* you are inspecting source;
* instructions say to download source;
* the project is pure Python and has clear run instructions.
Do not assume this ZIP is installable.
After extracting, check for:
README.md
requirements.txt
setup.py
pyproject.toml
main.py

6.3 When to Use Git Clone
Use git clone when:
* you have git installed;
* you need updates;
* you are developing the code;
* instructions explicitly say to clone;
* submodules or branches matter.
Command:
git clone https://github.com/user/project.git
cd project

On Windows PowerShell:
git clone https://github.com/user/project.git
cd project

If git is not installed, use Download ZIP instead.

6.4 Downloading a Specific Branch
A repository may have branches like:
main
master
dev
release
xp-compatible

Use the branch dropdown on GitHub before clicking Download ZIP.
If using git:
git clone -b branch-name https://github.com/user/project.git

Example:
git clone -b xp-compatible https://github.com/user/project.git

6.5 Downloading a Specific Tag or Version
Tags are usually safer than random current code.
Example:
git clone --branch v1.2.0 https://github.com/user/project.git

Without git:
GitHub → Tags → select version → Download ZIP

7. What File Should I Download?
7.1 Common File Types
.exe
    Windows installer or executable.

.msi
    Windows installer package.

.zip
    Compressed folder. May be ready-to-run or may be source code.

.7z
    Compressed archive. Requires 7-Zip or compatible tool.

.tar.gz
    Linux/source archive. Can be opened on Windows with 7-Zip.

.whl
    Python wheel package.

.tar.gz source package
    Python source distribution. May require build tools.

.py
    Python script.

.ps1
    PowerShell script.

.bat
    Windows batch script.

.sh
    Linux shell script.

.iso
    Disk image.

.dmg
    macOS disk image.

7.2 Python Wheel Names
Wheel files look like:
package_name-1.2.3-py3-none-any.whl
package_name-1.2.3-cp311-cp311-win_amd64.whl
package_name-1.2.3-cp27-cp27m-win32.whl

Interpretation:
py3-none-any
    Pure Python 3 package, any OS.

cp311
    CPython 3.11.

cp27
    CPython 2.7.

win_amd64
    64-bit Windows.

win32
    32-bit Windows.

manylinux
    Linux wheel.

armv7l / aarch64
    ARM Linux architecture, often relevant to Raspberry Pi.

For Windows XP / Python 2.7, a compatible wheel would usually need something like:
cp27
win32

Modern wheels usually will not support XP.

8. Python Install Basics
8.1 Preferred Command Form
Use:
python -m pip install package-name

or on Linux/Raspberry Pi:
python3 -m pip install package-name

This is better than:
pip install package-name

because it makes sure pip belongs to the Python you are using.

8.2 Check Python and Pip
Windows:
python --version
python -m pip --version

PowerShell:
python --version
python -m pip --version

Raspberry Pi/Linux:
python3 --version
python3 -m pip --version

If pip is missing, the fix depends heavily on the environment.
For modern Python:
python -m ensurepip --upgrade

or:
python3 -m ensurepip --upgrade

For Windows XP / Python 2.7, do not assume modern pip bootstrap instructions work.
Use known-good offline installers or packages for that environment.

9. Installing From a Requirements File
Many Python projects include:
requirements.txt

Install with:
python -m pip install -r requirements.txt

or:
python3 -m pip install -r requirements.txt

But first inspect it.
A requirements file may contain modern packages that are incompatible with XP, Raspberry Pi, or Pydroid.
Open it and look for suspicious dependencies:
PyQt6
PySide6
opencv-python
numpy
pandas
scipy
torch
tensorflow
modern-only packages

For constrained systems, install one package at a time if needed.

10. Installing a Local Wheel
If you downloaded:
package_name-1.2.3-py3-none-any.whl

install it from the folder containing the wheel:
python -m pip install package_name-1.2.3-py3-none-any.whl

On Raspberry Pi:
python3 -m pip install package_name-1.2.3-py3-none-any.whl

If there are multiple wheels in a folder:
python -m pip install *.whl

PowerShell may need:
python -m pip install (Get-ChildItem *.whl).FullName

11. Installing From a Downloaded Source Folder
If a downloaded project has:
setup.py

you may install from inside that folder:
python -m pip install .

If it has:
pyproject.toml

you may also install with:
python -m pip install .

For editable/development install:
python -m pip install -e .

Use editable install when you are modifying the code.
Do not use editable install for a simple end-user installation unless needed.

12. Virtual Environments
12.1 Modern Python
For modern Python, create an isolated environment:
python -m venv .venv

Activate on Windows Command Prompt:
.venv\Scripts\activate

Activate on PowerShell:
.\.venv\Scripts\Activate.ps1

Activate on Linux/Raspberry Pi:
source .venv/bin/activate

Then install:
python -m pip install -r requirements.txt

Deactivate:
deactivate

12.2 Windows XP / Python 2.7
Do not assume modern venv exists.
For XP/Python 2.7 projects, prefer one of these:
1. Use the known installed Python(x,y) environment.
2. Keep the project standard-library-only if possible.
3. Vendor small pure-Python dependencies inside the package if license allows.
4. Use known-good old installers.
5. Avoid modern pip workflows unless proven on that machine.

Document the exact working setup.

13. Offline Installation Workflow
Use this for Windows XP, lab machines, offline Raspberry Pis, or any machine without internet.
13.1 On an Online Machine
Create a folder:
offline_install_bundle/

Put inside:
package.zip
wheels/
installers/
drivers/
README_OFFLINE_INSTALL.md
diagnostic_harness.py

For Python packages, download wheels:
python -m pip download -r requirements.txt -d wheels

For one package:
python -m pip download package-name -d wheels

Important:
This downloads wheels for the online machine’s environment unless you specify target options.
For Windows XP/Python 2.7 or Raspberry Pi, this may not download compatible wheels automatically.

13.2 Transfer by USB
Copy:
offline_install_bundle/

to the target machine.
On the target machine:
cd path/to/offline_install_bundle

Install from local wheel folder:
python -m pip install --no-index --find-links=wheels -r requirements.txt

or:
python -m pip install --no-index --find-links=wheels package-name

If pip is not available, use environment-specific instructions.

13.3 Offline Install Manifest
Every offline bundle should include:
OFFLINE_INSTALL_MANIFEST
Target OS:
Target Python:
Target architecture:
Downloaded on:
Downloaded by:
Package source:
Expected install command:
Included wheels/installers:
Known limitations:
Test command:
Diagnostic command:

14. Windows XP Special Procedure
14.1 XP Rules
For XP/Python 2.7:
Do not use:
f-strings
pathlib
dataclasses
type annotations
Python 3-only libraries
modern PyQt/PySide
modern numpy/pandas unless known-compatible
modern pip assumptions

Prefer:
Python(x,y) 2.7.6.1
PyQt4 if already available
old matplotlib if already available
standard library
LabJackPython versions known to work
plain .bat launchers
offline ZIP packages

14.2 XP Package Layout
Use simple paths.
Example:
C:\XP_TOOLS\project_name\
├── START_HERE.txt
├── run_project.bat
├── diagnostic.bat
├── project_main.py
├── tools\
│   └── diagnostic_harness.py
└── docs\

Avoid:
deep folder paths
Unicode-heavy paths
very long filenames
paths with special punctuation

14.3 XP Batch Launcher
Example:
@echo off
cd /d "%~dp0"
python project_main.py
pause

Diagnostic launcher:
@echo off
cd /d "%~dp0"
python tools\diagnostic_harness.py
pause

14.4 XP Diagnostic Must Report
Python version
Python executable
OS version
Working directory
Package path
Import checks
GUI toolkit availability
LabJack import availability
Matplotlib availability
File read/write test

15. Raspberry Pi Procedure
15.1 Basic System Check
uname -a
cat /etc/os-release
python3 --version
python3 -m pip --version

15.2 Install System Packages First
Some Python packages need OS libraries.
Typical pattern:
sudo apt update
sudo apt install python3-pip python3-venv

For serial:
sudo apt install python3-serial

For Tkinter:
sudo apt install python3-tk

For matplotlib:
sudo apt install python3-matplotlib

For camera/OpenCV projects, target-specific instructions are needed.

15.3 Raspberry Pi Virtual Environment
cd ~/project_name
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

If system packages are preferred over pip packages, document that explicitly.

15.4 Raspberry Pi Hardware Permissions
Serial devices may require group membership:
groups

Common group:
dialout

Add user:
sudo usermod -a -G dialout $USER

Then reboot or log out/in.
USB devices may require udev rules.
Document device-specific requirements.

16. Arduino / ESP32 Procedure
16.1 Identify What Is Being Installed
Arduino/ESP32 work may involve:
Arduino IDE
board support package
USB serial driver
library ZIP
firmware .ino/.cpp files
Python serial monitor
PlatformIO project

16.2 Common Driver Issue
If the board does not appear as a serial port:
Check:
USB cable supports data, not charge-only
driver installed
correct board selected
correct port selected
device manager / lsusb sees device

Windows Device Manager:
Ports (COM & LPT)
Universal Serial Bus controllers
Other devices

Linux:
lsusb
ls /dev/tty*
dmesg | tail

16.3 Python Serial Check
python -m pip install pyserial

Test:
import serial.tools.list_ports

for port in serial.tools.list_ports.comports():
    print(port.device, port.description)

17. LabJack Procedure
17.1 Identify Device and Library
Record:
Device model:
U3 / U6 / T-series:
OS:
Python version:
LabJack driver installed:
Python module import:

Known U6 pattern in our work:
import u6

Do not assume:
from labjack import u6

unless verified.
17.2 LabJack Import Diagnostic
try:
    import u6
    print("PASS: import u6")
except Exception as exc:
    print("FAIL: import u6")
    print(repr(exc))

17.3 Device Connection Diagnostic
try:
    import u6
    d = u6.U6()
    print("PASS: opened U6")
    print(d)
    d.close()
except Exception as exc:
    print("FAIL: could not open U6")
    print(repr(exc))

18. PyVISA / Instrument-Control Procedure
18.1 Basic Install
Modern Python:
python -m pip install pyvisa

Backends vary.
Often needed:
python -m pip install pyvisa-py

But many instruments work better with vendor VISA runtime installed.
18.2 Check Resources
import pyvisa

rm = pyvisa.ResourceManager()
print(rm.list_resources())

If no instruments appear:
Check:
USB/LAN/GPIB cable
instrument interface settings
driver/runtime installed
VISA backend
IP address
firewall
GPIB adapter driver

18.3 Rule for Power Supplies
Never make first communication test energize outputs.
First test should be identity/query only:
*IDN?

Output-enable commands come later, after safe-state policy is defined.

19. Common Error Messages and What They Usually Mean
19.1 python is not recognized
Meaning:
Python is not on PATH, or Python is not installed.

Try:
where python

or locate python.exe.
Use full path:
C:\Python27\python.exe script.py

19.2 pip is not recognized
Use:
python -m pip --version

If that fails, pip may not be installed for that Python.

19.3 No module named ...
Meaning:
The package is not installed into the Python interpreter you are using.

Check:
python --version
python -m pip list
python -m pip show package-name

19.4 SyntaxError
Common causes:
Running Python 3 code on Python 2.
Running Python 2 code on Python 3.
Using modern syntax on old Python.

Check:
python --version

19.5 Permission denied
Common causes:
No write permission.
Trying to write inside protected folder.
Linux device permission issue.
File open in another program.

Try writing to a user folder.

19.6 Could not build wheels
Common causes:
No compatible prebuilt wheel.
Missing compiler.
Missing OS development libraries.
Package does not support target Python/OS.

On constrained systems, prefer prebuilt wheels or older compatible versions.

19.7 DLL load failed
Common causes:
Wrong architecture.
Missing runtime DLL.
Package incompatible with OS.
Driver missing.
Python 32/64-bit mismatch.

Check:
OS architecture
Python architecture
package wheel architecture
driver/runtime requirements

19.8 No matching distribution found
Common causes:
Package does not support this Python version.
Package does not support this OS/architecture.
pip is too old.
Internet index is unavailable.

For XP/Python 2.7, this is common with modern packages.

20. Safe Download Rules
Use official sources when possible:
Project GitHub
Project website
Python Package Index
Vendor driver page
Official release archive

Avoid:
random reupload sites
driver bundle sites
ad-heavy fake download buttons
unknown installers

For legacy software, archive sites may be necessary, but record the source and scan files where practical.

21. Checksum / Hash Verification
If a site provides SHA256:
Windows PowerShell:
Get-FileHash .\filename.zip -Algorithm SHA256

Linux/Raspberry Pi:
sha256sum filename.zip

Compare the result with the published hash.
For files we create internally, include hashes in the package manifest when useful.

22. Standard Install Procedure for Our Packages
For one of our delivered ZIP packages:
22.1 Extract
Extract the ZIP.
Make sure the internal folder name matches the ZIP name.
Example:
20260503_00_project_package.zip
20260503_00_project_package/

22.2 Read First
Open:
README_START_HERE.md
RUN_INSTRUCTIONS.md
TEST_INSTRUCTIONS.md
KNOWN_LIMITATIONS.md

22.3 Run Diagnostics Before the App
Modern Python:
python tools/diagnostic_harness.py

or:
python -m tools.diagnostic_harness

Windows XP:
python tools\diagnostic_harness.py

22.4 Run Smoke Test
python tools/package_smoke_test.py

22.5 Run the App
Use the documented command.
Examples:
python main.py

or:
python app.py

or use a provided launcher:
run_app.bat
run_app.ps1
run_app.sh

23. Standard Diagnostic Report to Copy Back
When asking for help, copy this:
INSTALL/ENVIRONMENT DIAGNOSTIC

Machine:
OS:
OS version:
32-bit or 64-bit:
Python command used:
Python version:
pip version:
Working directory:
Package folder:
Command run:
Full error message:

Files visible in folder:
[paste dir/ls output]

Diagnostic report path:
[paste path]

Important context:
[offline? XP? Raspberry Pi? Pydroid? hardware attached?]

Useful commands:
Windows Command Prompt:
cd
dir
python --version
python -m pip --version

PowerShell:
pwd
ls
python --version
python -m pip --version

Linux/Raspberry Pi:
pwd
ls
python3 --version
python3 -m pip --version

24. Standard Download Decision Tree
Need ready-to-run app?
    → Check GitHub Releases / vendor downloads first.

Need Python library?
    → Prefer pip install if online and compatible.
    → Prefer wheel if offline or target-specific.
    → Use source only if build tools and compatibility are known.

Need exact version?
    → Use GitHub release tag or PyPI version pin.

Need XP support?
    → Avoid modern packages.
    → Look for old installers/wheels/source compatible with Python 2.7 / win32.
    → Prefer known-good stack.

Need Raspberry Pi support?
    → Check architecture and OS packages.
    → Prefer apt packages for heavy compiled dependencies when appropriate.
    → Test on actual Pi.

Need Android/Pydroid support?
    → Use Pydroid-compatible packages.
    → Test directly on device.

Need hardware support?
    → Install driver first.
    → Verify vendor utility or simple identity query before app testing.

25. Recommended Package Documentation for Installability
Every serious package should include:
README_START_HERE.md
RUN_INSTRUCTIONS.md
TEST_INSTRUCTIONS.md
INSTALLATION_GUIDE.md
KNOWN_LIMITATIONS.md
DEPENDENCIES.md
OFFLINE_INSTALL_NOTES.md, if applicable
DRIVER_SETUP.md, if hardware is involved

Minimum DEPENDENCIES.md format:
Dependency:
Required/optional:
Purpose:
Install command:
Known-good version:
Target OS:
Target Python:
Fallback if missing:
Diagnostic check:

Minimum DRIVER_SETUP.md format:
Device:
Driver required:
Driver source:
Known-good version:
How to verify install:
How to identify device:
Troubleshooting:

26. Core Takeaways
1. Identify the target environment before downloading.
2. Prefer official releases over random source snapshots.
3. Use python -m pip, not bare pip, when possible.
4. Use wheels when offline or avoiding builds.
5. Do not assume modern Python instructions work on XP.
6. Do not assume Windows packages work on Raspberry Pi.
7. Do not assume desktop Python behavior works in Pydroid.
8. Run diagnostics before running complex apps.
9. Keep installers, wheels, drivers, and instructions together for offline machines.
10. Record what worked so the install can be repeated later.

Python Libraries
