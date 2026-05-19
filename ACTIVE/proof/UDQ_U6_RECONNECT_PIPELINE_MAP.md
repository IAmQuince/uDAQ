# U6 Reconnect Pipeline Map

1. device loss detected during poll
2. disconnect incident opened on the active real-U6 adapter
3. adapter is marked disconnected in lifecycle state and service inventory
4. bounded recovery polling continues for the disconnected active adapter
5. reconnect attempt starts
6. backend reopen either fails or succeeds
7. if backend reopen succeeds, a real post-disconnect poll is attempted
8. only after that successful post-disconnect poll does the adapter declare recovery
9. lifecycle handler emits `adapter_rebind_succeeded` and `device_recovered`

## Failure stages now surfaced
- `backend_reopen_failed`
- `post_disconnect_poll_failed`
- `device_loss_detected`

## Success stages now surfaced
- `backend_reopen_succeeded`
- `post_disconnect_poll_resumed`
- `adapter_rebind_succeeded`
- `device_recovered`
