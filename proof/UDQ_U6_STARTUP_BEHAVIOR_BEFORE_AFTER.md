# UDQ U6 Startup Behavior — Before vs After

## Before
- startup success or failure had to be inferred from health summary text and whether snapshots appeared
- no explicit startup classification lived with the adapter state

## After
- startup now records explicit classification such as `real_device_connected` or `real_device_unavailable`
- smoke/diag outputs surface lifecycle state and startup classification directly
- failed startup no longer looks like a vague unknown/ready condition
