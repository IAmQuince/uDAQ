# U6 Recovery Event Taxonomy

## Runtime events emitted for reconnect analysis
- `device_degraded`
- `device_disconnected`
- `device_reconnect_attempt_started`
- `backend_reopen_failed`
- `backend_reopen_succeeded`
- `post_disconnect_poll_resumed`
- `adapter_rebind_succeeded`
- `device_recovered`

## Event semantics
- `device_reconnect_attempt_started`: a bounded reconnect attempt was started for the disconnected active adapter
- `backend_reopen_failed`: the active adapter attempted to reopen the backend and failed
- `backend_reopen_succeeded`: the backend reopened, but recovery is not yet declared
- `post_disconnect_poll_resumed`: a real post-disconnect successful poll occurred
- `adapter_rebind_succeeded`: the active adapter re-entered the live polling lane
- `device_recovered`: the recovery incident closed successfully
