# UniversalDAQ Cross-Device Degraded Adapter Timeline

- simultaneous_drop_event_count: 1
- degraded_transition_count: 5
- adapters_seen_degraded: ['ARDUINO-UNO-ARD-401', 'LABJACK-U6-470201', 'RPI-RPI-LAB-401']

## Cycle transitions

- cycle=5 tick=604 action=drop adapters=['LABJACK-U6-470201', 'ARDUINO-UNO-ARD-401'] active_after=['RPI-RPI-LAB-401']
- cycle=6 tick=605 action=restore adapters=['LABJACK-U6-470201'] active_after=['LABJACK-U6-470201', 'RPI-RPI-LAB-401']
- cycle=7 tick=606 action=restore adapters=['ARDUINO-UNO-ARD-401'] active_after=['ARDUINO-UNO-ARD-401', 'LABJACK-U6-470201', 'RPI-RPI-LAB-401']
- cycle=9 tick=608 action=drop adapters=['RPI-RPI-LAB-401'] active_after=['ARDUINO-UNO-ARD-401', 'LABJACK-U6-470201']
- cycle=10 tick=609 action=restore adapters=['RPI-RPI-LAB-401'] active_after=['ARDUINO-UNO-ARD-401', 'LABJACK-U6-470201', 'RPI-RPI-LAB-401']
