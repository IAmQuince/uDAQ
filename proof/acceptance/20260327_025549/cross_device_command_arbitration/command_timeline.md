# UniversalDAQ Cross-Device Command Timeline

## Events

- t=601 output=labjack_u6_470201:digital_out_0 event=command_intent owner=manual summary=command intent admitted for bounded adapter dispatch
- t=601 output=labjack_u6_470201:digital_out_0 event=ownership_granted owner=manual summary=writer lease granted for accepted command
- t=602 output=labjack_u6_470201:digital_out_0 event=command_intent owner=manual summary=command intent admitted for bounded adapter dispatch
- t=602 output=labjack_u6_470201:digital_out_0 event=ownership_renewed owner=manual summary=writer lease renewed for same-owner superseding command
- t=603 output=labjack_u6_470201:digital_out_0 event=command_rejected_ownership_conflict owner=runtime summary=command rejected because another owner currently holds the writable lease
- t=603 output=rpi_rpi_lab_401:gpio_out_0 event=command_intent owner=runtime summary=command intent admitted for bounded adapter dispatch
- t=603 output=rpi_rpi_lab_401:gpio_out_0 event=ownership_granted owner=runtime summary=writer lease granted for accepted command
- t=604 output=arduino_uno_ard_401:digital_out_0 event=target_degraded owner= summary=adapter dropped out of the bounded command lane
- t=604 output=arduino_uno_ard_401:digital_out_0 event=command_rejected_unavailable owner=manual summary=command rejected because target is unavailable
- t=605 output=arduino_uno_ard_401:digital_out_0 event=target_restored owner= summary=adapter returned to the bounded command lane
- t=605 output=labjack_u6_470201:digital_out_0 event=lease_expired owner=manual summary=writer lease expired before the next command attempt
- t=605 output=arduino_uno_ard_401:digital_out_0 event=command_intent owner=manual summary=command intent admitted for bounded adapter dispatch
- t=605 output=arduino_uno_ard_401:digital_out_0 event=ownership_granted owner=manual summary=writer lease granted for accepted command
- t=606 output=labjack_u6_470201:digital_out_0 event=target_degraded owner= summary=adapter dropped out of the bounded command lane
- t=606 output=labjack_u6_470201:digital_out_0 event=safe_state_required owner= summary=target degraded and safe state required
- t=606 output=rpi_rpi_lab_401:gpio_out_0 event=target_degraded owner= summary=adapter dropped out of the bounded command lane
- t=606 output=rpi_rpi_lab_401:gpio_out_0 event=lease_revoked_on_degrade owner=runtime summary=degraded target revoked the active writer lease
- t=606 output=rpi_rpi_lab_401:gpio_out_0 event=command_rejected_unavailable owner=runtime summary=command rejected because target is unavailable
- t=607 output=labjack_u6_470201:digital_out_0 event=target_restored owner= summary=adapter returned to the bounded command lane
- t=607 output=rpi_rpi_lab_401:gpio_out_0 event=target_restored owner= summary=adapter returned to the bounded command lane
- t=607 output=labjack_u6_470201:digital_out_0 event=command_intent owner=runtime summary=command intent admitted for bounded adapter dispatch
- t=607 output=labjack_u6_470201:digital_out_0 event=ownership_granted owner=runtime summary=writer lease granted for accepted command
- t=608 output=arduino_uno_ard_401:digital_out_0 event=lease_expired owner=manual summary=writer lease expired before the next command attempt
- t=608 output=labjack_u6_470201:digital_out_0 event=command_rejected_ownership_conflict owner=manual summary=command rejected because another owner currently holds the writable lease
- t=609 output=arduino_uno_ard_401:digital_out_0 event=command_intent owner=supervisor summary=command intent admitted for bounded adapter dispatch
- t=609 output=arduino_uno_ard_401:digital_out_0 event=ownership_granted owner=supervisor summary=writer lease granted for accepted command
- t=609 output=rpi_rpi_lab_401:gpio_out_0 event=command_intent owner=runtime summary=command intent admitted for bounded adapter dispatch
- t=609 output=rpi_rpi_lab_401:gpio_out_0 event=ownership_granted owner=runtime summary=writer lease granted for accepted command
- t=610 output=labjack_u6_470201:digital_out_0 event=lease_expired owner=runtime summary=writer lease expired before the next command attempt
- t=610 output=arduino_uno_ard_401:digital_out_0 event=command_intent owner=supervisor summary=command intent admitted for bounded adapter dispatch
- t=610 output=arduino_uno_ard_401:digital_out_0 event=ownership_renewed owner=supervisor summary=writer lease renewed for same-owner superseding command
- t=611 output=arduino_uno_ard_401:digital_out_0 event=target_degraded owner= summary=adapter dropped out of the bounded command lane
- t=611 output=arduino_uno_ard_401:digital_out_0 event=lease_revoked_on_degrade owner=supervisor summary=degraded target revoked the active writer lease
- t=611 output=arduino_uno_ard_401:digital_out_0 event=command_rejected_unavailable owner=manual summary=command rejected because target is unavailable
