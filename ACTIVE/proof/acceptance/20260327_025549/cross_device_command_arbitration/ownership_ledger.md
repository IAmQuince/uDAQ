# UniversalDAQ Cross-Device Ownership Ledger

## Ownership lifecycle

- t=601 output=labjack_u6_470201:digital_out_0 event=ownership_granted owner=manual lease_expires_at= summary=writer lease granted for accepted command
- t=602 output=labjack_u6_470201:digital_out_0 event=ownership_renewed owner=manual lease_expires_at= summary=writer lease renewed for same-owner superseding command
- t=603 output=rpi_rpi_lab_401:gpio_out_0 event=ownership_granted owner=runtime lease_expires_at= summary=writer lease granted for accepted command
- t=605 output=labjack_u6_470201:digital_out_0 event=lease_expired owner=manual lease_expires_at= summary=writer lease expired before the next command attempt
- t=605 output=arduino_uno_ard_401:digital_out_0 event=ownership_granted owner=manual lease_expires_at= summary=writer lease granted for accepted command
- t=606 output=rpi_rpi_lab_401:gpio_out_0 event=lease_revoked_on_degrade owner=runtime lease_expires_at= summary=degraded target revoked the active writer lease
- t=607 output=labjack_u6_470201:digital_out_0 event=ownership_granted owner=runtime lease_expires_at= summary=writer lease granted for accepted command
- t=608 output=arduino_uno_ard_401:digital_out_0 event=lease_expired owner=manual lease_expires_at= summary=writer lease expired before the next command attempt
- t=609 output=arduino_uno_ard_401:digital_out_0 event=ownership_granted owner=supervisor lease_expires_at= summary=writer lease granted for accepted command
- t=609 output=rpi_rpi_lab_401:gpio_out_0 event=ownership_granted owner=runtime lease_expires_at= summary=writer lease granted for accepted command
- t=610 output=labjack_u6_470201:digital_out_0 event=lease_expired owner=runtime lease_expires_at= summary=writer lease expired before the next command attempt
- t=610 output=arduino_uno_ard_401:digital_out_0 event=ownership_renewed owner=supervisor lease_expires_at= summary=writer lease renewed for same-owner superseding command
- t=611 output=arduino_uno_ard_401:digital_out_0 event=lease_revoked_on_degrade owner=supervisor lease_expires_at= summary=degraded target revoked the active writer lease
