---
document_id: DOC-250
title: "LabJack U3/U6 LabJackPython Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-250
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# LabJack U3/U6 LabJackPython Guide

250_LABJACK_U3_U6_LABJACKPYTHON_GUIDE
0. Purpose
This guide explains how to use LabJack U3 and U6 devices from Python, especially the U6, using the correct legacy-device stack:
U3 / U6 / UE9
    → UD driver on Windows
    → LabJackPython
    → import u3 / import u6 / import ue9

Do not use LJM as the normal stack for U3/U6/UE9.
Use LJM for newer T-series devices:
T4 / T7 / T8 / Digit
    → LJM driver/library
    → labjack-ljm / Python_LJM
    → from labjack import ljm

LabJack’s documentation separates these software stacks: U3/U6/UE9 use the UD driver family, while T-series/Digit use LJM. LabJackPython is the Python module for U3, U6, UE9, and U12, and on Windows it uses the UD driver. (LabJack Support)

1. What a LabJack Does
A LabJack is a data-acquisition and control device. It lets a computer interact with real electrical signals.
Common tasks:
Read analog voltages.
Read sensors.
Read digital inputs.
Set digital outputs.
Set analog output voltages.
Count pulses.
Measure frequency.
Use timers.
Log data.
Control test fixtures.
Build simple DAQ/control systems.

The U6 is especially useful for precision analog measurements. LabJack describes the U6 analog inputs as software-selectable over ranges including ±10 V, ±1 V, ±0.1 V, and ±0.01 V, and notes that inputs can be read single-ended or differentially in even/odd pairs. (LabJack)

2. Correct Software Stack
2.1 U3 / U6 / UE9
Use:
UD driver / UD library
LabJackPython
LJControlPanel
LJLogUD
LJStreamUD

Typical Python imports:
import u3
import u6
import ue9

Use the import that matches the hardware.
2.2 T-Series / Digit
Use:
LJM driver/library
Kipling
labjack-ljm / Python_LJM

Typical Python import:
from labjack import ljm

This document is mainly about the U3/U6/LabJackPython side.

3. Install and Verify
3.1 Install UD driver
Install the LabJack UD software package for U3/U6/UE9 from LabJack’s official support/download area.
After installation, verify with:
LJControlPanel

The device should appear before Python is involved.
3.2 Install LabJackPython
Modern Python, if supported:
python -m pip install LabJackPython

For older systems, especially Windows XP / Python 2.7, use the known-good old LabJackPython package and UD driver version for that machine.
3.3 Verify U6 import
try:
    import u6
    print("PASS: import u6")
except Exception as exc:
    print("FAIL: import u6")
    print(repr(exc))

3.4 Verify U6 connection
import u6

d = u6.U6()
print(d.configU6())
d.close()

Expected result:
A dictionary containing device information such as serial number, firmware version, hardware version, local ID, and device name.

The LabJackPython U6 class is designed to open and work with a U6 directly, and its source examples show the common import u6 / u6.U6() pattern. (GitHub)

4. U6 Analog Input Basics
4.1 Simple single-ended analog input
This reads AIN0 relative to ground.
import u6

d = u6.U6()

try:
    volts = d.getAIN(0)
    print("AIN0 = %.6f V" % volts)
finally:
    d.close()

Use this first.
Do not start with all channels, differential mode, thermocouples, or streaming. Confirm one simple voltage first.

5. Reading One Input with Settings
The U6 getAIN convenience function supports important analog-input settings:
getAIN(
    positiveChannel,
    resolutionIndex=0,
    gainIndex=0,
    settlingFactor=0,
    differential=False
)

LabJackPython’s U6 source describes these parameters as: resolutionIndex, gainIndex, settlingFactor, and differential; it also documents gain index values of x1, x10, x100, x1000, and an autorange option. (GitHub)
5.1 Read AIN0 on ±10 V range
import u6

d = u6.U6()

try:
    volts = d.getAIN(
        positiveChannel=0,
        resolutionIndex=0,
        gainIndex=0,
        settlingFactor=0,
        differential=False
    )
    print("AIN0 ±10V range = %.6f V" % volts)
finally:
    d.close()

Settings:
positiveChannel=0
    Read AIN0.

resolutionIndex=0
    Default behavior.

gainIndex=0
    x1 gain, ±10 V range.

settlingFactor=0
    Automatic settling.

differential=False
    Single-ended reading relative to ground.

6. Gain / Range Settings
For U6 analog inputs:
gainIndex=0
    x1 gain, ±10 V range.

gainIndex=1
    x10 gain, ±1 V range.

gainIndex=2
    x100 gain, ±0.1 V range.

gainIndex=3
    x1000 gain, ±0.01 V range.

gainIndex=15
    Autorange, where supported by the command.

LabJack’s U6 analog-input docs describe range/gain as synonymous and list the UD constants for ±10 V, ±1 V, ±0.1 V, and ±0.01 V ranges. (LabJack Support)
Practical rule:
Use the smallest range that safely contains the signal.

Examples:
0 to 5 V sensor:
    gainIndex=0, ±10 V range.

0 to 100 mV signal:
    gainIndex=2, ±0.1 V range.

Thermocouple signal:
    usually gainIndex=2, ±0.1 V range, differential.

Do not choose a small range if the signal may exceed it.

7. Resolution Index
The resolution index trades speed for resolution/noise performance.
LabJack’s U6 documentation states that valid resolution index values are 0–8 for the U6 and 0–12 for the U6-Pro, and that increasing the resolution index generally improves resolution while increasing sample time. It also notes that resolution index values 9–12 apply only to the U6-Pro. (LabJack Support)
Practical interpretation:
resolutionIndex=0
    Default. Good first choice.

resolutionIndex=1 to 4
    Faster, lower resolution.

resolutionIndex=8
    High-resolution command/response reading on normal U6.

resolutionIndex=9 to 12
    U6-Pro high-resolution ADC only, command/response mode.

Example high-resolution read on a normal U6:
import u6

d = u6.U6()

try:
    volts = d.getAIN(
        positiveChannel=0,
        resolutionIndex=8,
        gainIndex=0,
        settlingFactor=0,
        differential=False
    )
    print("AIN0 high-resolution = %.9f V" % volts)
finally:
    d.close()

Use higher resolution for slow precision measurements.
Use lower resolution for faster measurement.

8. Settling Factor
Settling factor gives the analog front end more time to settle after switching channels/ranges.
LabJackPython documents these U6 settling factor meanings:
0 = Auto
1 = 20 us
2 = 50 us
3 = 100 us
4 = 200 us
5 = 500 us
6 = 1 ms
7 = 2 ms
8 = 5 ms
9 = 10 ms

Use higher settling when:
source impedance is high
external filters are present
switching between channels with very different voltages
readings look wrong immediately after channel changes
low-level signals need more stability

Example:
import u6

d = u6.U6()

try:
    volts = d.getAIN(
        positiveChannel=0,
        resolutionIndex=8,
        gainIndex=0,
        settlingFactor=6,   # 1 ms
        differential=False
    )
    print("AIN0 with 1 ms settling = %.9f V" % volts)
finally:
    d.close()

9. Differential Analog Input
Differential mode measures the voltage difference between two analog inputs.
For U6 command/response reads, normal differential pairs are adjacent even/odd channels:
AIN0 - AIN1
AIN2 - AIN3
AIN4 - AIN5
AIN6 - AIN7
AIN8 - AIN9
AIN10 - AIN11
AIN12 - AIN13

LabJack’s U6 analog input documentation states that differential channels are adjacent even/odd pairs, where the positive channel is even and the negative channel is the next channel. (LabJack Support)
Example:
import u6

d = u6.U6()

try:
    volts = d.getAIN(
        positiveChannel=0,
        resolutionIndex=8,
        gainIndex=2,        # ±0.1 V range
        settlingFactor=0,
        differential=True   # AIN0 - AIN1
    )
    print("AIN0-AIN1 = %.9f V" % volts)
finally:
    d.close()

Important:
differential=True with positiveChannel=0 reads AIN0 - AIN1.
differential=True with positiveChannel=2 reads AIN2 - AIN3.

10. Reading All Analog Inputs
This is useful after one-channel reads are working.
import time
import u6

d = u6.U6()

try:
    while True:
        for ch in range(14):
            try:
                volts = d.getAIN(ch)
                print("AIN%-2d = % .6f V" % (ch, volts))
            except Exception as exc:
                print("AIN%-2d read failed: %r" % (ch, exc))

        print("-" * 40)
        time.sleep(1.0)

except KeyboardInterrupt:
    print("Stopping.")

finally:
    d.close()

Use this for a quick wiring survey.
Do not use this as the final structure for a real DAQ system. For a serious system, use named channel mapping:
AIN0 → stack_voltage
AIN1 → current_monitor
AIN2-AIN3 → thermocouple_1

11. Reading a Named Channel
A cleaner pattern:
import u6

CHANNEL_MAP = {
    "stack_voltage": {
        "positiveChannel": 0,
        "resolutionIndex": 0,
        "gainIndex": 0,
        "settlingFactor": 0,
        "differential": False,
        "units": "V",
    },
    "thermocouple_voltage": {
        "positiveChannel": 2,
        "resolutionIndex": 8,
        "gainIndex": 2,
        "settlingFactor": 6,
        "differential": True,
        "units": "V",
    },
}

def read_named_channel(device, name):
    cfg = CHANNEL_MAP[name]
    return device.getAIN(
        positiveChannel=cfg["positiveChannel"],
        resolutionIndex=cfg["resolutionIndex"],
        gainIndex=cfg["gainIndex"],
        settlingFactor=cfg["settlingFactor"],
        differential=cfg["differential"],
    )

d = u6.U6()

try:
    for name in CHANNEL_MAP:
        value = read_named_channel(d, name)
        print("%s = %.9f %s" % (name, value, CHANNEL_MAP[name]["units"]))
finally:
    d.close()

This is better than hardcoding raw channel numbers everywhere.

12. U6 Analog Outputs: DAC0 and DAC1
The U6 has two analog outputs:
DAC0
DAC1

LabJack describes the U6 DAC outputs as analog outputs available on screw terminals and DB37, settable between about 0 and 5 V with 12-bit resolution; analog outputs are updated in command/response mode. (LabJack)
12.1 Simple raw DAC output
LabJackPython provides feedback commands such as:
u6.DAC0_8(value)
u6.DAC1_8(value)
u6.DAC0_16(value)
u6.DAC1_16(value)

The LabJackPython U6 source documents DAC8 as using values 0–255 and DAC16 as using values 0–65535. (GitHub)
Example using raw 16-bit command value:
import time
import u6

d = u6.U6()

try:
    # Approximate mid-scale.
    d.getFeedback(u6.DAC0_16(32768))
    print("Set DAC0 to approximately mid-scale.")
    time.sleep(2.0)

    # Back near zero.
    d.getFeedback(u6.DAC0_16(0))
    print("Set DAC0 near 0 V.")
finally:
    d.close()

This is useful for confirming DAC behavior.
For real voltage control, use a helper.

13. Setting DAC Voltage with Calibration Helper
The U6 stores calibration constants. LabJackPython loads calibration data when the U6 opens unless told otherwise; the U6 source includes DAC calibration slope/offset data and DAC feedback commands. (GitHub)
This helper converts a desired voltage to a DAC16 command value using the device calibration data.
import time
import u6

def clamp(value, low, high):
    return max(low, min(high, value))

def volts_to_dac16_value(device, dac_number, volts):
    """
    Convert desired DAC voltage to a DAC16 command value using U6 calibration.

    dac_number:
        0 for DAC0
        1 for DAC1

    volts:
        Desired voltage, normally about 0 to 5 V.
    """
    volts = clamp(float(volts), 0.0, 5.0)

    slope = device.calInfo.dacSlope[dac_number]
    offset = device.calInfo.dacOffset[dac_number]

    raw = int(volts * slope + offset)
    raw = int(clamp(raw, 0, 65535))
    return raw

def set_dac_voltage(device, dac_number, volts):
    raw = volts_to_dac16_value(device, dac_number, volts)

    if dac_number == 0:
        device.getFeedback(u6.DAC0_16(raw))
    elif dac_number == 1:
        device.getFeedback(u6.DAC1_16(raw))
    else:
        raise ValueError("dac_number must be 0 or 1")

    return raw

d = u6.U6()

try:
    for volts in [0.0, 1.0, 2.5, 4.0, 0.0]:
        raw = set_dac_voltage(d, 0, volts)
        print("DAC0 requested %.3f V, raw command %d" % (volts, raw))
        time.sleep(1.0)
finally:
    try:
        set_dac_voltage(d, 0, 0.0)
        set_dac_voltage(d, 1, 0.0)
    finally:
        d.close()

Safety rule:
Always set DAC outputs to a known safe value before exiting if the output controls hardware.

14. Reading DAC Output Back Through AIN
A simple loopback test:
DAC0 → AIN0
GND  → GND

Then run:
import time
import u6

def clamp(value, low, high):
    return max(low, min(high, value))

def volts_to_dac16_value(device, dac_number, volts):
    volts = clamp(float(volts), 0.0, 5.0)
    slope = device.calInfo.dacSlope[dac_number]
    offset = device.calInfo.dacOffset[dac_number]
    return int(clamp(volts * slope + offset, 0, 65535))

def set_dac_voltage(device, dac_number, volts):
    raw = volts_to_dac16_value(device, dac_number, volts)
    if dac_number == 0:
        device.getFeedback(u6.DAC0_16(raw))
    else:
        device.getFeedback(u6.DAC1_16(raw))
    return raw

d = u6.U6()

try:
    for target in [0.5, 1.0, 2.0, 3.0, 4.0]:
        set_dac_voltage(d, 0, target)
        time.sleep(0.1)
        measured = d.getAIN(0)
        print("Target DAC0 %.3f V, measured AIN0 %.6f V" % (target, measured))

    set_dac_voltage(d, 0, 0.0)

finally:
    d.close()

Do this before using DAC outputs to control anything important.

15. Digital I/O Basics
The U6 has digital I/O lines such as FIO, EIO, CIO/MIO. LabJack’s U6 product page states that the U6 has 20 digital I/O channels individually configurable as input, output-high, or output-low. (LabJack)
LabJackPython provides convenience functions common to U3 and U6 such as:
setDOState
getDIState
getDIOState
getAIN
getTemperature

LabJack’s low-level command quickstart explicitly identifies these convenience functions for U3/U6. (LabJack Support)
15.1 Set a digital output
import time
import u6

d = u6.U6()

try:
    # FIO4 is digital I/O number 4.
    d.setDOState(4, 1)
    print("FIO4 high")
    time.sleep(1.0)

    d.setDOState(4, 0)
    print("FIO4 low")
finally:
    d.close()

15.2 Read a digital input
import u6

d = u6.U6()

try:
    state = d.getDIState(4)
    print("FIO4 input state =", state)
finally:
    d.close()

15.3 Read digital state without changing direction
import u6

d = u6.U6()

try:
    state = d.getDIOState(4)
    print("FIO4 current state =", state)
finally:
    d.close()

Use getDIState when you want to force the line to input.
Use getDIOState when you want to read the current state without changing direction.

16. U6 Temperature Sensor
The U6 has an internal temperature sensor near the AIN0–AIN3 screw terminals. LabJack notes that this sensor is useful for thermocouple cold junction compensation and has maximum accuracy around ±2 °C. (LabJack)
Basic read:
import u6

d = u6.U6()

try:
    temp_c = d.getTemperature()
    print("Internal temperature = %.3f C" % temp_c)
finally:
    d.close()

Use this for:
rough board/local temperature
cold junction compensation estimate
diagnostics

For better thermocouple accuracy, use a better cold-junction temperature measurement near the actual terminal junction.

17. Thermocouple Measurement with U6
17.1 Why thermocouples are different
A thermocouple produces a very small voltage.
For a Type K thermocouple near room temperature, the signal is roughly:
about 40 microvolts per °C

This is tiny compared with normal 0–5 V sensors.
A thermocouple measurement needs:
low-noise differential voltage measurement
small input range
cold junction compensation
secure wiring
appropriate conversion from voltage to temperature

LabJack’s thermocouple app note describes thermocouples as responsive, low-cost, wide-range temperature sensors, but notes that if measuring only -50 to +150 °C, a silicon temperature sensor should be considered instead. (LabJack Support)

17.2 Recommended U6 wiring for a Type K thermocouple
LabJack’s U6 thermocouple tutorial recommends a differential connection between AIN0 and AIN1, with a 10–100 kΩ resistor and Type K thermocouple. The tutorial specifically shows thermocouple+ to AIN0, thermocouple- to AIN1, and a 100 kΩ resistor from AIN1 to GND. (LabJack Support)
Use:
Thermocouple+ → AIN0
Thermocouple- → AIN1
100 kΩ resistor → AIN1 to GND

Then read:
AIN0 - AIN1

Do not leave the differential input floating.

17.3 Recommended U6 settings for thermocouple voltage
LabJack’s U6 thermocouple tutorial says to use differential mode and set the gain/range to BI 0.1 V, which corresponds to the ±0.1 V range and x100 gain. It also notes that resolution 0 maps to index 8 on a normal U6 or index 9 on a U6-Pro. (LabJack Support)
Python read:
import u6

d = u6.U6()

try:
    tc_volts = d.getAIN(
        positiveChannel=0,
        resolutionIndex=8,
        gainIndex=2,        # x100, ±0.1 V
        settlingFactor=6,   # 1 ms; useful conservative starting point
        differential=True   # AIN0 - AIN1
    )

    print("Thermocouple voltage = %.9f V" % tc_volts)
    print("Thermocouple voltage = %.3f uV" % (tc_volts * 1e6))

finally:
    d.close()

Expected sanity check:
With the thermocouple tip near the U6 terminals, voltage should be near 0 V.
Warming the tip should increase the voltage for Type K.

LabJack’s tutorial says the voltage should increase by roughly 40 μV per °C when the remote end is warmed relative to the U6 end. (LabJack Support)

17.4 Rough thermocouple temperature estimate
This is only a rough teaching/debug estimate.
def rough_type_k_delta_c_from_volts(tc_volts):
    """
    Very rough near-room-temperature Type K approximation.

    Type K near room temperature is about 40 uV/C.
    This gives temperature difference between hot junction and cold junction.
    """
    return tc_volts / 40e-6

Example:
import u6

d = u6.U6()

try:
    cold_junction_c = d.getTemperature()

    tc_volts = d.getAIN(
        positiveChannel=0,
        resolutionIndex=8,
        gainIndex=2,
        settlingFactor=6,
        differential=True
    )

    delta_c = rough_type_k_delta_c_from_volts(tc_volts)
    estimated_tip_c = cold_junction_c + delta_c

    print("Cold junction estimate = %.2f C" % cold_junction_c)
    print("Thermocouple voltage   = %.3f uV" % (tc_volts * 1e6))
    print("Delta estimate         = %.2f C" % delta_c)
    print("Tip estimate           = %.2f C" % estimated_tip_c)

finally:
    d.close()

Use this to see if the signal makes sense.
Do not use this as final calibrated thermocouple conversion.
For serious thermocouple work, use proper NIST thermocouple polynomials or a verified thermocouple library and a better cold-junction temperature measurement if accuracy matters.

17.5 Thermocouple accuracy caution
LabJack notes that CJC error matters directly: any error in the cold junction temperature appears as error in the thermocouple temperature. Their U6 thermocouple tutorial says to expect about ±2 °C using the internal temperature sensor, or about ±0.5 °C using an LM34CAZ temperature sensor. (LabJack Support)
Practical rule:
Internal U6 temperature sensor:
    good for rough CJC and diagnostics.

External temperature sensor near the thermocouple terminals:
    better for accurate thermocouple work.

18. Current Outputs
The U6 has fixed current outputs:
10 uA
200 uA

LabJack notes these are useful for measuring resistors, thermistors, and RTDs. (LabJack)
Typical concept:
current source → resistor/sensor → ground
measure voltage across sensor
R = V / I

Example for 200 μA:
If I = 200 μA and V = 1.000 V:

R = 1.000 / 0.000200
R = 5000 Ω

This can be useful for:
thermistors
RTDs
resistive sensors
continuity-ish measurements

Do not exceed voltage/current limits or assume the current source is appropriate for every sensor.

19. Basic CSV Logger
import csv
import os
import time
import u6

CHANNELS = [
    {
        "name": "AIN0_single",
        "positiveChannel": 0,
        "resolutionIndex": 0,
        "gainIndex": 0,
        "settlingFactor": 0,
        "differential": False,
    },
    {
        "name": "AIN2_diff_low_level",
        "positiveChannel": 2,
        "resolutionIndex": 8,
        "gainIndex": 2,
        "settlingFactor": 6,
        "differential": True,
    },
]

def safe_makedirs(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)

def read_channel(device, cfg):
    return device.getAIN(
        positiveChannel=cfg["positiveChannel"],
        resolutionIndex=cfg["resolutionIndex"],
        gainIndex=cfg["gainIndex"],
        settlingFactor=cfg["settlingFactor"],
        differential=cfg["differential"],
    )

def main():
    safe_makedirs("runtime_data")
    path = os.path.join("runtime_data", "u6_log.csv")

    d = u6.U6()

    try:
        with open(path, "w", newline="") as f:
            fieldnames = ["timestamp"] + [c["name"] for c in CHANNELS]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            print("Logging to", path)
            print("Press Ctrl+C to stop.")

            while True:
                row = {"timestamp": time.time()}

                for cfg in CHANNELS:
                    try:
                        row[cfg["name"]] = read_channel(d, cfg)
                    except Exception as exc:
                        row[cfg["name"]] = ""
                        print("Read failed for %s: %r" % (cfg["name"], exc))

                writer.writerow(row)
                f.flush()

                print(row)
                time.sleep(1.0)

    except KeyboardInterrupt:
        print("Stopping.")

    finally:
        d.close()

if __name__ == "__main__":
    main()

This is a reasonable starting point for a simple logger.
For serious DAQ software, add:
threaded acquisition
writer queue
quality flags
channel map JSON
diagnostic report
safe shutdown
fault logging

20. U6 Diagnostic Script
Save as:
tools/u6_diagnostic.py

import os
import sys
import time
import traceback

def main():
    lines = []
    lines.append("LABJACK U6 DIAGNOSTIC REPORT")
    lines.append("=" * 72)
    lines.append("timestamp: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("python: %s" % sys.version)
    lines.append("cwd: %s" % os.getcwd())
    lines.append("")

    try:
        import u6
        lines.append("import u6: PASS")
    except Exception:
        lines.append("import u6: FAIL")
        lines.append(traceback.format_exc())
        print("\n".join(lines))
        return

    d = None

    try:
        d = u6.U6()
        lines.append("open U6: PASS")
        lines.append("configU6:")
        lines.append(str(d.configU6()))
        lines.append("")

        try:
            temp_c = d.getTemperature()
            lines.append("internal_temperature_c: %.3f" % temp_c)
        except Exception:
            lines.append("internal temperature read failed:")
            lines.append(traceback.format_exc())

        lines.append("")
        lines.append("analog inputs:")
        for ch in range(4):
            try:
                volts = d.getAIN(ch)
                lines.append("AIN%d = %.6f V" % (ch, volts))
            except Exception:
                lines.append("AIN%d read failed:" % ch)
                lines.append(traceback.format_exc())

        lines.append("")
        lines.append("DAC loopback reminder:")
        lines.append("To test DAC output, wire DAC0 to AIN0 and run a DAC loopback script.")

    except Exception:
        lines.append("U6 diagnostic failed:")
        lines.append(traceback.format_exc())

    finally:
        if d is not None:
            try:
                d.close()
            except Exception:
                pass

    report_dir = "diagnostics"
    if not os.path.isdir(report_dir):
        os.makedirs(report_dir)

    path = os.path.join(report_dir, "u6_diagnostic_report.txt")

    with open(path, "w") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))
    print("")
    print("Wrote:", path)

if __name__ == "__main__":
    main()

Run:
python tools\u6_diagnostic.py

21. Common Problems
21.1 import u6 fails
Likely causes:
LabJackPython is not installed.
Wrong Python environment is active.
Python version is incompatible with installed package.
UD driver is missing on Windows.

Check:
python --version
python -m pip show LabJackPython
python -c "import u6; print('u6 ok')"

21.2 U6 does not open
Likely causes:
UD driver not installed.
USB cable problem.
Device not powered.
Another program has the device open.
Wrong device family assumptions.

Check with:
LJControlPanel

before debugging Python.
21.3 Readings are noisy
Check:
signal source impedance
grounding
shielding
range/gain setting
resolution index
settling factor
differential vs single-ended wiring
floating input
bad thermocouple wiring

21.4 Thermocouple reads nonsense
Check:
thermocouple polarity
differential pair
bias resistor to ground
gainIndex=2 / ±0.1 V range
resolutionIndex high enough
cold junction temperature
secure terminals
real temperature gradients near terminals

21.5 DAC output not expected
Check:
DAC0/DAC1 wiring
GND reference
load impedance
raw DAC command vs calibrated voltage helper
multimeter reading
loopback to AIN
safe output state on exit

22. Safety Rules
Do not connect unknown voltages to AIN.
Do not exceed analog input limits.
Do not drive external loads directly from DAC outputs unless the load is appropriate.
Do not use DAC outputs as power supplies.
Do not connect 5 V logic into non-tolerant digital inputs without checking limits.
Do not assume thermocouple wires are noise-free.
Do not assume a floating differential input will read correctly.
Always test with LJControlPanel before Python.
Always set outputs to a safe state on exit.

23. Minimal Acceptance Tests
A LabJack U6 setup is ready for project work when:
[ ] UD driver installed.
[ ] LJControlPanel sees the U6.
[ ] Python can import u6.
[ ] Python can open u6.U6().
[ ] configU6 returns device information.
[ ] AIN0 can read a known voltage.
[ ] DAC0 can be set and measured with a meter or loopback.
[ ] Digital output can toggle a safe test line.
[ ] Digital input can read a known high/low state.
[ ] Diagnostic report can be generated.
[ ] For thermocouples, AIN0-AIN1 differential test behaves correctly.

24. Core Rules
RULE-LJ-001
U3/U6/UE9 use UD + LabJackPython, not LJM.

RULE-LJ-002
T4/T7/T8/Digit use LJM + labjack-ljm, not LabJackPython/u6.

RULE-LJ-003
Verify hardware in LJControlPanel before debugging Python.

RULE-LJ-004
Start with one analog input before scanning many inputs.

RULE-LJ-005
Use named channel maps for serious DAQ work.

RULE-LJ-006
Use the smallest safe input range for better low-level voltage measurement.

RULE-LJ-007
Higher resolution index improves resolution but slows readings.

RULE-LJ-008
Differential U6 inputs normally use even/odd adjacent pairs.

RULE-LJ-009
Thermocouples require differential measurement and cold junction compensation.

RULE-LJ-010
DAC outputs must be returned to safe values on exit if connected to real hardware.

25. Closing Principle
For our LabJack work, the standard progression is:
install correct driver
verify with LabJack utility
verify Python import
open device
read one analog input
read with explicit settings
test DAC output safely
test digital I/O
build named channel map
add logging
add diagnostics
add safe shutdown

The U6 is powerful because it can read ordinary voltages, low-level differential signals, thermocouples, digital lines, DAC outputs, timers, and counters. But it only stays manageable if the setup is explicit:
device family
driver stack
Python module
channel map
range/gain
resolution
settling
wiring
calibration
diagnostics
safe output state

Microcontrollers
