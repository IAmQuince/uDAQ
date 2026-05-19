---
document_id: DOC-240
title: "MIDI, Python, and Computer Instrument-Control Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-240
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# MIDI, Python, and Computer Instrument-Control Guide

240_MIDI_PYTHON_AND_COMPUTER_INSTRUMENT_CONTROL_GUIDE
0. Purpose
This document formalizes how we use MIDI with Python and computers.
It covers:
* MIDI hardware setup;
* USB MIDI devices;
* 5-pin DIN MIDI;
* TRS MIDI Type A / Type B issues;
* virtual MIDI ports;
* modern Windows MIDI workflows;
* Windows XP / legacy MIDI workflows;
* Python libraries such as Mido, python-rtmidi, and pygame.midi;
* routing MIDI between devices and software;
* using MIDI controllers to control Python programs;
* sending notes and controller messages to synths or DAWs;
* logging MIDI data;
* avoiding feedback loops and stuck notes;
* building diagnostic tools.
This applies to projects involving:
* MIDI keyboards;
* MIDI controllers;
* Launchkey-style controllers;
* M-Audio / Midiman MIDI interfaces;
* USB MIDI devices;
* 5-pin DIN MIDI gear;
* software synths;
* REAPER or other DAWs;
* Python simulation control;
* Python lighting/music/hardware experiments;
* old Windows XP audio/MIDI systems;
* modern Windows Python MIDI tools.
The goal is not only to “play notes.”
The goal is to treat MIDI as a general-purpose real-time control protocol between humans, computers, instruments, and software.

1. What MIDI Is
MIDI stands for Musical Instrument Digital Interface.
MIDI is not audio.
MIDI is control data.
A MIDI message can say things like:
note 60 turned on
note 60 turned off
control knob 21 moved to value 93
pitch bend changed
switch program to instrument 12
start clock
stop playback

The sound is produced somewhere else:
software synth
hardware synth
DAW instrument track
sampler
drum machine
lighting controller
custom Python program

This distinction matters.
If a MIDI keyboard makes no sound, that does not necessarily mean MIDI is broken. It may simply mean the MIDI signal is working but no instrument is assigned to receive it.

2. Core MIDI Concepts
2.1 MIDI device
A MIDI device is anything that sends or receives MIDI.
Examples:
keyboard controller
drum pad controller
knob/fader controller
synthesizer
drum machine
MIDI interface
DAW
Python program
virtual MIDI port

2.2 MIDI input
A MIDI input receives MIDI messages.
Example:
Python listening to a Launchkey Mini
REAPER listening to a MIDI keyboard
synth receiving notes from a sequencer

2.3 MIDI output
A MIDI output sends MIDI messages.
Example:
Python sending notes to a synth
keyboard sending notes to REAPER
DAW sending clock to a drum machine

2.4 MIDI channel
Traditional MIDI has 16 channels:
1 through 16

In Python/Mido, channels are usually zero-based:
MIDI channel 1 → channel=0
MIDI channel 2 → channel=1
...
MIDI channel 16 → channel=15

This off-by-one issue is common.
Document whether a program is showing user-facing channel numbers or Python/Mido internal channel numbers.
2.5 Note number
MIDI notes are numeric.
Common reference:
60 = middle C / C4 in many systems

However, octave naming can vary between software packages. The note number is the reliable value.
2.6 Velocity
Velocity usually means how hard a key or pad was struck.
Range:
0 to 127

For note messages:
note_on velocity 0

is often treated like:
note_off

Many controllers use this convention.
2.7 Control Change / CC
Control Change messages are used for knobs, sliders, pedals, buttons, modulation, and general control.
A CC message has:
channel
control number
value

Example:
control 21 moved to value 93

Range:
control number: 0 to 127
value: 0 to 127

2.8 Program Change
Program Change messages select a patch, preset, or instrument program.
Example:
program_change program=12

2.9 Pitch Bend
Pitch bend changes pitch smoothly.
Pitch bend usually has a center value and ranges upward/downward.
In Mido, pitch wheel messages use values roughly in this range:
-8192 to 8191

2.10 MIDI Clock
MIDI clock is used to synchronize tempo between devices.
Important messages:
clock
start
stop
continue
song_position

A MIDI clock sends 24 clock pulses per quarter note.
For most Python projects, do not implement clock handling until basic note/CC input works.

3. MIDI 1.0 vs MIDI 2.0
Most practical Python MIDI projects still use MIDI 1.0-style messages, ports, and files.
MIDI 2.0 exists and extends MIDI 1.0 rather than simply replacing it. The MIDI Association describes MIDI 2.0 as an extension that builds on MIDI 1.0 principles and semantics. For our typical Python workflows, assume MIDI 1.0 unless the hardware/software explicitly requires MIDI 2.0. (MIDI.org)
Practical rule:
For our Python MIDI projects:
    Start with MIDI 1.0.
    Use Mido/python-rtmidi.
    Treat MIDI 2.0 as a future/specialty case.

4. Physical MIDI Connections
4.1 USB MIDI
Many modern controllers connect directly by USB.
Example:
Launchkey Mini → USB cable → computer

The device appears as a MIDI input and/or output port.
Common problems:
charge-only USB cable
driver missing
device not powered
wrong port selected
DAW already owns the port
Python using wrong backend

4.2 5-pin DIN MIDI
Traditional MIDI uses 5-pin DIN connectors.
Important direction rule:
MIDI OUT on device A → MIDI IN on device B

For two-way communication:
Device A OUT → Device B IN
Device B OUT → Device A IN

MIDI THRU passes a copy of incoming MIDI onward.
4.3 MIDI interface
A MIDI interface converts between USB and 5-pin DIN MIDI.
Example:
computer USB
    ↓
M-Audio / Midiman interface
    ↓
5-pin DIN MIDI OUT
    ↓
hardware synth MIDI IN

Common issue:
The interface has multiple input/output ports.
The DAW/Python program must select the correct one.

4.4 TRS MIDI Type A and Type B
Some smaller devices use 3.5 mm TRS MIDI instead of 5-pin DIN.
There are two common wiring types:
Type A
Type B

Type A is the current official TRS MIDI standard adopted by the MIDI Association, but some manufacturers and older devices use Type B. If two devices use opposite types, a normal cable/adaptor may not work; the tip/ring wiring must match or be converted. (Morningstar Engineering)
Practical rule:
Do not guess TRS MIDI type.

Check the device manual:
    Type A?
    Type B?
    manufacturer-specific adapter?

This matters for gear from companies such as Novation, Arturia, 1010music, Elektron, Korg, Make Noise, and others. The exact type depends on the device.

5. Virtual MIDI Ports
5.1 What virtual MIDI ports do
A virtual MIDI port lets one program send MIDI to another program on the same computer.
Example:
Python program
    → virtual MIDI output
        → REAPER input
            → software synth

Or:
REAPER
    → virtual MIDI output
        → Python program

5.2 loopMIDI on Windows
loopMIDI is a common Windows tool for creating virtual loopback MIDI ports. Its documentation describes it as a virtual loopback MIDI cable for Windows that lets applications communicate through hardware-MIDI-port-like connections. (Tobias Erichsen)
Typical use:
1. Open loopMIDI.
2. Create a port, for example: Python_To_REAPER.
3. In Python, open output port Python_To_REAPER.
4. In REAPER, enable Python_To_REAPER as a MIDI input.

Important:
loopMIDI ports exist while loopMIDI is running.
If loopMIDI is closed, the ports disappear.

5.3 Virtual ports through RtMidi
Mido’s RtMidi backend can create virtual ports in some environments. Mido’s documentation notes that RtMidi is the backend that can create virtual ports. (Mido)
Practical rule:
On Windows:
    loopMIDI is usually the simplest virtual port method.

On Linux/macOS:
    RtMidi/ALSA/JACK/CoreMIDI virtual-port behavior may be enough.

6. Python MIDI Library Choices
6.1 Mido
Mido is the primary high-level Python MIDI library for our modern Python MIDI work.
It provides:
MIDI messages
MIDI input ports
MIDI output ports
MIDI file reading/writing
message parsing
backend-independent port API

Mido’s docs describe it as a Python library for MIDI 1.0 ports, messages, and files. (Mido)
Use Mido when:
you want readable Python MIDI code
you are routing messages
you are monitoring controllers
you are sending notes/CCs
you are making MIDI files
you are writing modern Python tools

Install:
python -m pip install mido

For live ports, also install a backend.
6.2 python-rtmidi
python-rtmidi is the usual modern backend to pair with Mido.
Install:
python -m pip install python-rtmidi

The python-rtmidi documentation includes utilities for listing and opening MIDI input/output ports, and PyPI currently states that python-rtmidi supports Python 3.8+. (Spotlight Kid)
Use this stack for modern Windows:
mido
python-rtmidi
loopMIDI, if virtual ports are needed

6.3 pygame.midi
pygame.midi is useful for:
legacy workflows
Pygame projects
simple input/output tests
Windows XP-era experiments
PortMidi-style MIDI access

Pygame’s docs say pygame.midi can send output to MIDI devices, get input from MIDI devices, list MIDI devices, and supports real and virtual MIDI devices through PortMidi. (Pygame)
Install:
python -m pip install pygame

Use pygame.midi when:
Mido backend installation is difficult
Pygame is already part of the project
working in a legacy-style environment
you want simple port listing and basic I/O

6.4 rtmidi direct
You can use python-rtmidi directly without Mido.
Use direct rtmidi when:
you need lower-level control
you are debugging backend behavior
you are building a minimal diagnostic

For most of our code, Mido is cleaner.
6.5 pyserial for custom microcontroller MIDI-like protocols
If an Arduino/ESP32 is sending messages over serial rather than true USB MIDI, use:
pyserial

Install:
python -m pip install pyserial

This is not the same as class-compliant MIDI. It is serial data that may represent musical/control events.
Use pyserial when:
Arduino sends JSON lines
ESP32 sends sensor/controller packets
microcontroller is not exposing a true MIDI port

7. Standard Modern Windows Install
Recommended modern Windows MIDI stack:
python -m pip install mido python-rtmidi

Optional:
python -m pip install pygame

For virtual MIDI routing:
Install loopMIDI.
Create named ports.
Use Mido to open those ports.
Use DAW/software synth to receive them.

Verification:
python -c "import mido; print(mido.__version__)"
python -c "import rtmidi; print('rtmidi ok')"
python -c "import pygame.midi; print('pygame.midi ok')"

8. Windows XP / Legacy MIDI Notes
For Windows XP / Python 2.7 projects, do not assume modern Mido/python-rtmidi will install.
Current python-rtmidi is a modern Python 3 package. Use legacy versions only if they are known to work on the target machine.
For XP-era MIDI projects, likely approaches are:
older Pygame + pygame.midi
older PortMidi-based tools
older Mido versions only if verified
manufacturer MIDI drivers
DAW-based routing

XP rule:
Do not design XP MIDI projects around current pip packages.
Use the actual installed Python version and known-good legacy installers.

Recommended XP diagnostic:
from __future__ import print_function

try:
    import pygame
    import pygame.midi
    print("pygame:", pygame.version.ver)
    pygame.midi.init()
    print("MIDI devices:", pygame.midi.get_count())
    pygame.midi.quit()
except Exception as exc:
    print("pygame.midi failed:", repr(exc))

9. Common MIDI Workflows
9.1 Monitor a controller
Goal:
See what notes, pads, knobs, sliders, and buttons are sending.

Useful for:
mapping controller controls
debugging MIDI input
building MIDI learn
checking channels and CC numbers

9.2 Route input to output
Goal:
Take MIDI from one device and send it somewhere else.

Example:
Launchkey Mini input
    → Python filter/remapper
        → loopMIDI output
            → REAPER

9.3 Map knobs to Python parameters
Goal:
Use MIDI controller knobs/sliders to control a Python simulation or hardware program.

Examples:
CC 21 controls rain density
CC 22 controls particle speed
CC 23 controls light brightness
CC 24 controls DAQ graph time window

9.4 Send notes to a synth
Goal:
Python generates note_on/note_off messages.
A synth or DAW instrument turns those into sound.

9.5 Record MIDI input to CSV
Goal:
Preserve every incoming MIDI event with timestamp, message type, note/CC/value/channel.

Useful for:
analyzing timing
debugging controllers
training control mappings
recording performances

9.6 Create or edit MIDI files
Mido can create and save Standard MIDI Files. Mido’s MIDI file docs show creating a MidiFile, appending tracks/messages, and saving the file. (Mido)
Use this when:
generating test sequences
creating note patterns
exporting algorithmic music
building MIDI examples

9.7 Use MIDI as an operator control surface
Goal:
Use a physical MIDI controller as a cheap, rugged, flexible hardware interface.

Examples:
faders control variables
pads trigger actions
knobs tune parameters
transport buttons start/stop simulations
keys trigger notes or commands

This can be useful outside music.

10. Mido Basic Port Diagnostic
Save as:
tools/midi_port_diagnostic.py

import sys
import mido

def main():
    print("MIDI Port Diagnostic")
    print("=" * 72)
    print("Python:", sys.version)
    print("Mido:", getattr(mido, "__version__", "unknown"))
    print("Backend:", mido.backend)
    print("")

    print("Input ports:")
    try:
        for name in mido.get_input_names():
            print("  IN :", name)
    except Exception as exc:
        print("  Failed listing input ports:", repr(exc))

    print("")

    print("Output ports:")
    try:
        for name in mido.get_output_names():
            print("  OUT:", name)
    except Exception as exc:
        print("  Failed listing output ports:", repr(exc))

    print("")
    print("Done.")

if __name__ == "__main__":
    main()

Run:
python tools\midi_port_diagnostic.py

If no ports appear:
confirm device is plugged in
confirm driver is installed
confirm DAW is not exclusively holding the port
try loopMIDI if virtual routing is needed
try pygame.midi diagnostic

11. Force Mido RtMidi Backend
In many modern projects, explicitly use RtMidi.
import mido

mido.set_backend("mido.backends.rtmidi")

print("Backend:", mido.backend)
print("Inputs:", mido.get_input_names())
print("Outputs:", mido.get_output_names())

Alternative environment-variable approach:
set MIDO_BACKEND=mido.backends.rtmidi
python your_script.py

PowerShell:
$env:MIDO_BACKEND="mido.backends.rtmidi"
python your_script.py

12. Monitor Incoming MIDI with Mido
import mido

def main():
    mido.set_backend("mido.backends.rtmidi")

    inputs = mido.get_input_names()

    if not inputs:
        print("No MIDI input ports found.")
        return

    print("Available input ports:")
    for i, name in enumerate(inputs):
        print("[%d] %s" % (i, name))

    index = int(input("Select input index: "))
    port_name = inputs[index]

    print("Opening:", port_name)
    print("Move knobs, press keys, or hit pads. Ctrl+C to quit.")

    with mido.open_input(port_name) as inport:
        for msg in inport:
            print(msg)

if __name__ == "__main__":
    main()

Expected output examples:
note_on channel=0 note=60 velocity=100 time=0
note_off channel=0 note=60 velocity=64 time=0
control_change channel=0 control=21 value=93 time=0
pitchwheel channel=0 pitch=1024 time=0

13. Send a Note with Mido
import time
import mido

def main():
    mido.set_backend("mido.backends.rtmidi")

    outputs = mido.get_output_names()

    if not outputs:
        print("No MIDI output ports found.")
        return

    print("Available output ports:")
    for i, name in enumerate(outputs):
        print("[%d] %s" % (i, name))

    index = int(input("Select output index: "))
    port_name = outputs[index]

    with mido.open_output(port_name) as outport:
        note = 60
        velocity = 90
        channel = 0

        print("Sending note_on")
        outport.send(mido.Message("note_on", note=note, velocity=velocity, channel=channel))

        time.sleep(1.0)

        print("Sending note_off")
        outport.send(mido.Message("note_off", note=note, velocity=0, channel=channel))

if __name__ == "__main__":
    main()

Important:
Always send note_off.

If note_off is not sent, notes can stick.

14. Panic / All Notes Off
Always include a panic function in serious MIDI programs.
import mido

def panic(outport):
    for channel in range(16):
        outport.send(mido.Message("control_change", channel=channel, control=123, value=0))
        outport.send(mido.Message("control_change", channel=channel, control=120, value=0))

        for note in range(128):
            outport.send(mido.Message("note_off", channel=channel, note=note, velocity=0))

Common controls:
CC 123 = All Notes Off
CC 120 = All Sound Off

Not every device responds perfectly, so explicit note_off loops are useful.
Use panic when:
program exits
user presses emergency key
port is closing
feedback loop occurs
exception happens

15. MIDI Router with Filter
This receives from one port and sends to another port.
import mido

def should_forward(msg):
    if msg.type == "clock":
        return False
    if msg.type == "active_sensing":
        return False
    return True

def main():
    mido.set_backend("mido.backends.rtmidi")

    inputs = mido.get_input_names()
    outputs = mido.get_output_names()

    if not inputs:
        print("No input ports.")
        return

    if not outputs:
        print("No output ports.")
        return

    print("Inputs:")
    for i, name in enumerate(inputs):
        print("[%d] %s" % (i, name))

    in_index = int(input("Input index: "))

    print("Outputs:")
    for i, name in enumerate(outputs):
        print("[%d] %s" % (i, name))

    out_index = int(input("Output index: "))

    with mido.open_input(inputs[in_index]) as inport, mido.open_output(outputs[out_index]) as outport:
        print("Routing. Ctrl+C to stop.")
        for msg in inport:
            if should_forward(msg):
                outport.send(msg)
                print("forwarded:", msg)
            else:
                print("filtered:", msg)

if __name__ == "__main__":
    main()

This is the basic Python MIDI router.
Add mapping/remapping after this works.

16. Remap Controller CC to Another CC
import mido

CC_MAP = {
    21: 74,
    22: 71,
    23: 73,
}

def remap_message(msg):
    if msg.type == "control_change":
        if msg.control in CC_MAP:
            return msg.copy(control=CC_MAP[msg.control])
    return msg

def main():
    mido.set_backend("mido.backends.rtmidi")

    in_name = mido.get_input_names()[0]
    out_name = mido.get_output_names()[0]

    with mido.open_input(in_name) as inport, mido.open_output(out_name) as outport:
        for msg in inport:
            mapped = remap_message(msg)
            outport.send(mapped)
            print(msg, "→", mapped)

if __name__ == "__main__":
    main()

Use this when a controller’s knob numbers do not match the target software or synth.

17. MIDI Learn Pattern
MIDI learn means:
The user moves a knob or presses a control.
The program remembers which MIDI message that was.
Then the program maps that control to an action.

Example:
import mido

def learn_control(input_port_name):
    print("Move the control you want to learn...")

    with mido.open_input(input_port_name) as inport:
        for msg in inport:
            if msg.type in ("control_change", "note_on", "note_off"):
                print("Learned:", msg)
                return {
                    "type": msg.type,
                    "channel": getattr(msg, "channel", None),
                    "control": getattr(msg, "control", None),
                    "note": getattr(msg, "note", None),
                }

def matches_mapping(msg, mapping):
    if msg.type != mapping["type"]:
        return False

    if mapping["channel"] is not None and getattr(msg, "channel", None) != mapping["channel"]:
        return False

    if mapping["control"] is not None and getattr(msg, "control", None) != mapping["control"]:
        return False

    if mapping["note"] is not None and getattr(msg, "note", None) != mapping["note"]:
        return False

    return True

Use MIDI learn for configurable control surfaces.
Save learned mappings to JSON:
import json

def save_mapping(path, mapping):
    with open(path, "w") as f:
        json.dump(mapping, f, indent=2, sort_keys=True)

def load_mapping(path):
    with open(path, "r") as f:
        return json.load(f)

18. Map MIDI CC to Simulation Parameter
def scale_0_127(value, low, high):
    return low + (value / 127.0) * (high - low)

def handle_midi_for_simulation(msg, sim_state):
    if msg.type != "control_change":
        return

    if msg.control == 21:
        sim_state["rain_density"] = scale_0_127(msg.value, 1.0, 300.0)

    elif msg.control == 22:
        sim_state["rain_speed"] = scale_0_127(msg.value, 10.0, 1000.0)

    elif msg.control == 23:
        sim_state["wind_speed"] = scale_0_127(msg.value, -500.0, 500.0)

    elif msg.control == 24:
        sim_state["particle_size"] = scale_0_127(msg.value, 1.0, 20.0)

This is the pattern for using a MIDI controller as a real-time parameter panel.
Useful for:
Pygame simulations
lighting control
audio visualization
DAQ display tuning
hardware test station operator controls

19. Threaded MIDI Input Pattern
Do not block the GUI or main simulation loop while waiting for MIDI input.
Use a MIDI thread that writes to a queue.
import queue
import threading
import time
import traceback

import mido

class MidiInputThread(threading.Thread):
    def __init__(self, port_name, message_queue, event_queue, shutdown_event):
        threading.Thread.__init__(self)
        self.daemon = False
        self.port_name = port_name
        self.message_queue = message_queue
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.messages_received = 0
        self.last_error = ""

    def run(self):
        try:
            with mido.open_input(self.port_name) as inport:
                self.event_queue.put({
                    "type": "midi_open",
                    "port": self.port_name,
                    "timestamp": time.time(),
                })

                while not self.shutdown_event.is_set():
                    for msg in inport.iter_pending():
                        self.messages_received += 1
                        self.message_queue.put({
                            "timestamp": time.time(),
                            "message": msg,
                        })

                    time.sleep(0.005)

        except Exception as exc:
            self.last_error = repr(exc)
            self.event_queue.put({
                "type": "midi_error",
                "port": self.port_name,
                "error": repr(exc),
                "traceback": traceback.format_exc(),
                "timestamp": time.time(),
            })

    def diagnostics(self):
        return {
            "thread": "MidiInputThread",
            "alive": self.is_alive(),
            "port_name": self.port_name,
            "messages_received": self.messages_received,
            "last_error": self.last_error,
        }

Main loop:
midi_queue = queue.Queue()
event_queue = queue.Queue()
shutdown_event = threading.Event()

thread = MidiInputThread("YOUR MIDI INPUT PORT", midi_queue, event_queue, shutdown_event)
thread.start()

try:
    while True:
        try:
            item = midi_queue.get(timeout=0.1)
            print(item["timestamp"], item["message"])
        except queue.Empty:
            pass

except KeyboardInterrupt:
    shutdown_event.set()
    thread.join()

Rule:
MIDI thread receives messages.
Main/UI thread consumes messages.
Do not update GUI widgets directly from the MIDI thread.

20. Threaded MIDI Output Pattern
For serious programs, output should also go through a queue.
import queue
import threading
import time
import traceback

import mido

class MidiOutputThread(threading.Thread):
    def __init__(self, port_name, command_queue, event_queue, shutdown_event):
        threading.Thread.__init__(self)
        self.daemon = False
        self.port_name = port_name
        self.command_queue = command_queue
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.messages_sent = 0
        self.last_error = ""
        self.outport = None

    def run(self):
        try:
            with mido.open_output(self.port_name) as outport:
                self.outport = outport

                self.event_queue.put({
                    "type": "midi_output_open",
                    "port": self.port_name,
                    "timestamp": time.time(),
                })

                while not self.shutdown_event.is_set() or not self.command_queue.empty():
                    try:
                        msg = self.command_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    outport.send(msg)
                    self.messages_sent += 1

                self.panic(outport)

        except Exception as exc:
            self.last_error = repr(exc)
            self.event_queue.put({
                "type": "midi_output_error",
                "port": self.port_name,
                "error": repr(exc),
                "traceback": traceback.format_exc(),
                "timestamp": time.time(),
            })

    def panic(self, outport):
        for channel in range(16):
            outport.send(mido.Message("control_change", channel=channel, control=123, value=0))
            outport.send(mido.Message("control_change", channel=channel, control=120, value=0))

    def diagnostics(self):
        return {
            "thread": "MidiOutputThread",
            "alive": self.is_alive(),
            "port_name": self.port_name,
            "messages_sent": self.messages_sent,
            "last_error": self.last_error,
        }

Main code sends commands:
command_queue.put(mido.Message("note_on", note=60, velocity=100))
command_queue.put(mido.Message("note_off", note=60, velocity=0))

21. MIDI Logging to CSV
import csv
import os
import time

import mido

def message_to_row(timestamp, msg):
    return {
        "timestamp": "%.6f" % timestamp,
        "type": msg.type,
        "channel": getattr(msg, "channel", ""),
        "note": getattr(msg, "note", ""),
        "velocity": getattr(msg, "velocity", ""),
        "control": getattr(msg, "control", ""),
        "value": getattr(msg, "value", ""),
        "program": getattr(msg, "program", ""),
        "pitch": getattr(msg, "pitch", ""),
        "raw": str(msg),
    }

def log_midi_input(port_name, csv_path):
    folder = os.path.dirname(os.path.abspath(csv_path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    fieldnames = [
        "timestamp",
        "type",
        "channel",
        "note",
        "velocity",
        "control",
        "value",
        "program",
        "pitch",
        "raw",
    ]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        with mido.open_input(port_name) as inport:
            for msg in inport:
                ts = time.time()
                row = message_to_row(ts, msg)
                writer.writerow(row)
                f.flush()
                print(row)

if __name__ == "__main__":
    mido.set_backend("mido.backends.rtmidi")
    print("Inputs:", mido.get_input_names())
    port = mido.get_input_names()[0]
    log_midi_input(port, "runtime_data/midi_log.csv")

Use this before building complicated mappings.
The log tells you exactly what the controller sends.

22. Create a MIDI File with Mido
from mido import Message, MidiFile, MidiTrack

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

track.append(Message("program_change", program=0, time=0))
track.append(Message("note_on", note=60, velocity=90, time=0))
track.append(Message("note_off", note=60, velocity=0, time=480))
track.append(Message("note_on", note=64, velocity=90, time=0))
track.append(Message("note_off", note=64, velocity=0, time=480))
track.append(Message("note_on", note=67, velocity=90, time=0))
track.append(Message("note_off", note=67, velocity=0, time=480))

mid.save("example_chord_arpeggio.mid")

This creates a standard .mid file.
You can open it in:
REAPER
MuseScore
DAW
MIDI player
other sequencer

23. Play a MIDI File Out a Port
import mido
import time

def play_midi_file(filename, output_port_name):
    mid = mido.MidiFile(filename)

    with mido.open_output(output_port_name) as outport:
        for msg in mid.play():
            if not msg.is_meta:
                outport.send(msg)

if __name__ == "__main__":
    mido.set_backend("mido.backends.rtmidi")

    print("Outputs:", mido.get_output_names())
    output = mido.get_output_names()[0]

    play_midi_file("example_chord_arpeggio.mid", output)

The receiving device must be able to produce sound.
If sending to a virtual port, the DAW must be listening on that port and have an instrument loaded.

24. pygame.midi Port Diagnostic
import pygame
import pygame.midi

def main():
    pygame.init()
    pygame.midi.init()

    count = pygame.midi.get_count()
    print("pygame.midi device count:", count)

    for device_id in range(count):
        info = pygame.midi.get_device_info(device_id)
        interface, name, is_input, is_output, opened = info

        print("")
        print("ID:", device_id)
        print("Interface:", interface)
        print("Name:", name)
        print("Input:", bool(is_input))
        print("Output:", bool(is_output))
        print("Opened:", bool(opened))

    pygame.midi.quit()
    pygame.quit()

if __name__ == "__main__":
    main()

Use this when Mido cannot see ports or when working in a Pygame-based project.

25. pygame.midi Note Output
import time
import pygame
import pygame.midi

def main():
    pygame.init()
    pygame.midi.init()

    output_id = pygame.midi.get_default_output_id()
    print("Default output ID:", output_id)

    if output_id == -1:
        print("No MIDI output available.")
        return

    out = pygame.midi.Output(output_id)

    instrument = 0
    channel = 0
    note = 60
    velocity = 100

    out.set_instrument(instrument, channel)
    out.note_on(note, velocity, channel)
    time.sleep(1.0)
    out.note_off(note, 0, channel)

    del out
    pygame.midi.quit()
    pygame.quit()

if __name__ == "__main__":
    main()

This is useful for quick sanity checks.

26. Using MIDI with REAPER
Typical Python-to-REAPER route:
Python
    → Mido output
        → loopMIDI port
            → REAPER MIDI input
                → armed track
                    → instrument plugin

REAPER checklist:
[ ] loopMIDI is running.
[ ] Virtual port exists.
[ ] REAPER Preferences → MIDI Devices sees the port.
[ ] Port is enabled for input/control as needed.
[ ] Track input is set to the MIDI port.
[ ] Track is armed.
[ ] Input monitoring is enabled.
[ ] Instrument plugin is loaded.
[ ] Correct MIDI channel is accepted.

Common no-sound causes:
MIDI is arriving but no instrument is loaded.
Track is not armed.
Input monitoring is off.
Wrong port selected.
Wrong MIDI channel.
Audio driver/output not configured.

Common feedback cause:
REAPER MIDI output is routed back into the same input path.

Avoid routing:
Controller → REAPER → loopMIDI → Python → same REAPER input

unless a controlled loop is explicitly intended.

27. MIDI Feedback Loop Warning
A MIDI feedback loop can happen when output is routed back to input.
Symptoms:
notes repeat rapidly
controller lights behave strangely
DAW meter goes wild
latency increases
program floods messages
sound becomes stuck or chaotic

Fix:
disconnect one route
disable MIDI output back to controller
turn off track MIDI echo
close Python router
use panic/all-notes-off
restart loopMIDI if needed

In REAPER, be careful with:
MIDI input monitoring
MIDI hardware output
control surface settings
track routing
loopMIDI ports

Rule:
Do not connect a MIDI output back to its own input unless the program explicitly prevents feedback.

28. Using MIDI to Control Python Hardware/DAQ/Simulation Tools
MIDI can be used as a physical control surface.
Examples:
knob controls graph time window
fader controls target current
pad triggers marker event
transport play starts sequence preview
transport stop requests safe stop
key triggers simulated particle burst
mod wheel controls wind speed
pitch bend controls offset

Important for hardware-control projects:
MIDI input should request actions.
Hardware command thread should execute actions.
MIDI callback should not directly command dangerous hardware.

Safe architecture:
MIDI input thread
    → event queue
        → application controller
            → safety/state machine
                → hardware command queue

Unsafe architecture:
MIDI callback
    → direct power supply command

For DAQ/control work, always preserve:
operator state
command log
safe-state override
fault handling
diagnostics

29. MIDI as a Control Surface Mapping File
Use JSON mapping files.
Example:
{
  "mappings": [
    {
      "name": "rain_density",
      "type": "control_change",
      "channel": 0,
      "control": 21,
      "target": "simulation.rain_density",
      "scale_low": 1.0,
      "scale_high": 300.0
    },
    {
      "name": "safe_stop",
      "type": "note_on",
      "channel": 0,
      "note": 36,
      "target": "control.safe_stop",
      "trigger_velocity_min": 1
    }
  ]
}

Benefits:
controller can change without rewriting code
mappings can be saved per project
MIDI learn can update mapping file
documentation is easier

30. MIDI Timing Notes
Do not assume normal Python timing is sample-accurate.
Python MIDI is usually fine for:
control surfaces
parameter changes
interactive triggering
logging
routing
lightweight generative music
simulation control

Be careful for:
tight drum sequencing
sub-millisecond timing
professional live clock generation
hard real-time performance

For high-timing-precision music production, let the DAW or hardware sequencer handle tight timing where possible.
Python can still generate, modify, log, and route MIDI effectively.

31. Standard MIDI Diagnostic Report
Save as:
tools/midi_diagnostic_report.py

import os
import sys
import time
import traceback

REPORT_DIR = "diagnostics"

def safe_makedirs(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)

def check_import(name):
    try:
        __import__(name)
        return "PASS"
    except Exception as exc:
        return "FAIL: %r" % exc

def main():
    safe_makedirs(REPORT_DIR)

    lines = []
    lines.append("MIDI DIAGNOSTIC REPORT")
    lines.append("=" * 72)
    lines.append("timestamp: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("python: %s" % sys.version)
    lines.append("cwd: %s" % os.getcwd())
    lines.append("")

    lines.append("IMPORT CHECKS")
    lines.append("-" * 72)
    for module in ["mido", "rtmidi", "pygame", "pygame.midi", "serial"]:
        lines.append("%s: %s" % (module, check_import(module)))
    lines.append("")

    try:
        import mido

        lines.append("MIDO")
        lines.append("-" * 72)
        lines.append("version: %s" % getattr(mido, "__version__", "unknown"))

        try:
            mido.set_backend("mido.backends.rtmidi")
            lines.append("backend set to: %s" % mido.backend)
        except Exception as exc:
            lines.append("backend set failed: %r" % exc)

        lines.append("")
        lines.append("Input ports:")
        try:
            for name in mido.get_input_names():
                lines.append("  IN : %s" % name)
        except Exception:
            lines.append(traceback.format_exc())

        lines.append("")
        lines.append("Output ports:")
        try:
            for name in mido.get_output_names():
                lines.append("  OUT: %s" % name)
        except Exception:
            lines.append(traceback.format_exc())

        lines.append("")

    except Exception:
        lines.append("Mido section failed:")
        lines.append(traceback.format_exc())

    try:
        import pygame
        import pygame.midi

        lines.append("PYGAME.MIDI")
        lines.append("-" * 72)

        pygame.init()
        pygame.midi.init()

        count = pygame.midi.get_count()
        lines.append("device_count: %s" % count)

        for device_id in range(count):
            info = pygame.midi.get_device_info(device_id)
            lines.append("device %s: %r" % (device_id, info))

        pygame.midi.quit()
        pygame.quit()
        lines.append("")

    except Exception:
        lines.append("pygame.midi section failed:")
        lines.append(traceback.format_exc())

    path = os.path.join(REPORT_DIR, "midi_diagnostic_report.txt")
    with open(path, "w") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))
    print("")
    print("Wrote:", path)

if __name__ == "__main__":
    main()

This is the file to run before guessing.

32. Recommended Project Structure
midi_project/
├── README_START_HERE.md
├── RUN_INSTRUCTIONS.md
├── INSTALLATION.md
├── main.py
├── requirements.txt
├── config/
│   ├── midi_ports.json
│   └── midi_mappings.json
├── logs/
│   └── midi_events.csv
├── diagnostics/
│   └── midi_diagnostic_report.txt
├── tools/
│   ├── midi_diagnostic_report.py
│   ├── midi_port_monitor.py
│   ├── midi_router.py
│   └── midi_panic.py
└── midi_app/
    ├── __init__.py
    ├── ports.py
    ├── messages.py
    ├── routing.py
    ├── mapping.py
    ├── logging_utils.py
    ├── diagnostics.py
    └── app.py

33. Requirements Files
Modern Windows baseline:
mido
python-rtmidi

Optional:
pygame
pyserial

Example requirements_midi_modern.txt:
mido
python-rtmidi
pygame
pyserial

Install:
python -m pip install -r requirements_midi_modern.txt

XP/legacy:
Do not use a modern requirements file blindly.
Use known-good legacy installers and exact versions.

34. Common Problems and Fixes
No MIDI input ports
Check:
device plugged in
USB cable supports data
driver installed
device powered
DAW not holding port exclusively
correct backend installed
try pygame.midi diagnostic
restart program after plugging device in

No MIDI output ports
Check:
loopMIDI running
software synth installed/open
DAW enabled port
hardware synth connected
MIDI interface output selected

Python sees port but DAW does not
Check:
loopMIDI running
port created before DAW launched
DAW MIDI preferences refreshed
port enabled as input
track armed
input monitoring enabled

DAW sees MIDI but no sound
Check:
instrument plugin loaded
track armed
input monitoring on
audio output configured
MIDI channel accepted
note range valid

Stuck notes
Use:
panic/all notes off
close/reopen MIDI port
stop DAW playback
disable feedback loop
send note_off for all notes

MIDI feedback
Check:
Python output is not routed back into its own input.
DAW track is not echoing to same port.
Controller is not receiving and retransmitting same messages.

Wrong knob numbers
Run MIDI monitor.
Move one knob at a time.
Record:
message type
channel
control number
value range

Then update mapping JSON.
TRS MIDI cable does not work
Check:
Type A or Type B?
Correct adapter?
MIDI OUT to MIDI IN?
Device actually supports MIDI over TRS, not audio only?

Latency
Separate issues:
MIDI latency
audio buffer latency
DAW monitoring latency
Python processing delay
USB driver delay

If notes trigger late but MIDI messages arrive on time, the issue may be audio driver/buffer size rather than MIDI.

35. Acceptance Tests
A MIDI project is acceptable when:
[ ] MIDI diagnostic lists expected input ports.
[ ] MIDI diagnostic lists expected output ports.
[ ] Controller messages can be monitored.
[ ] Output notes can be sent and stopped.
[ ] Panic/all-notes-off works.
[ ] Virtual port routing works if needed.
[ ] DAW receives messages if DAW integration is required.
[ ] Mapping file is documented.
[ ] Stuck-note handling exists.
[ ] Feedback-loop risk is documented.
[ ] Port names are configurable.
[ ] Program can run with missing MIDI device and report the problem cleanly.
[ ] Logs can be generated for incoming messages.

36. Core Rules
RULE-MIDI-001
MIDI is control data, not audio.

RULE-MIDI-002
Always verify ports before debugging musical behavior.

RULE-MIDI-003
Always include a panic/all-notes-off path.

RULE-MIDI-004
Do not directly command dangerous hardware from a MIDI callback.

RULE-MIDI-005
Use Mido + python-rtmidi for modern Python MIDI work.

RULE-MIDI-006
Use pygame.midi as a useful fallback/legacy/Pygame path.

RULE-MIDI-007
Use loopMIDI for simple Windows virtual routing.

RULE-MIDI-008
Log incoming MIDI before building complex mappings.

RULE-MIDI-009
Avoid feedback loops.

RULE-MIDI-010
For XP/legacy systems, use known-good old versions, not current pip assumptions.

37. Closing Principle
MIDI is a practical real-time control layer.
For our projects, it can be:
a musical interface
a controller surface
a parameter-tuning panel
a DAW bridge
a simulation controller
a lighting controller
a hardware-control input layer
a diagnostic/logging stream

The standard progression is:
install MIDI stack
list ports
monitor input
send simple output
route through virtual port
log messages
map controls
build application behavior
add diagnostics
add panic/safety handling

That is the repeatable workflow to carry forward.

I2C
