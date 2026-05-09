# UniversalDAQ Canonical Tags

This package defines the **read-side canonical tag surface** used to normalize values from multiple adapter families into a single core representation.

The core rules are:
- the universal core speaks in canonical tags and normalized samples only
- device families are translated at the adapter boundary
- the multi-adapter broker is capability-based, not brand-based
- this slice is intentionally read-only; cross-device command arbitration is deferred
