# UDQ U6 Lifecycle Contract

## Bounded lifecycle states
- `configured` — adapter created but no backend connection attempted yet
- `initializing` — backend acquisition in progress
- `ready` — backend connected and current poll path healthy
- `degraded` — runtime read failure observed, bounded recovery attempt still possible
- `disconnected` — backend unavailable or runtime loss persisted beyond the first failure
- `faulted` — close/shutdown or adapter-internal error path encountered
- `stopped` — adapter explicitly closed

## Startup classifications
- `not_attempted`
- `real_device_connected`
- `real_device_unavailable`
- `real_device_reconnected`
- `real_device_reconnect_failed`
- `real_device_recovered`
- `runtime_read_failed`
- `runtime_device_lost`
- `shutdown_failed`

## Bounded transition model
- `configured -> initializing -> ready` on successful startup
- `configured -> initializing -> disconnected` on startup failure
- `ready -> degraded` on first runtime read failure
- `degraded -> ready` on bounded recovery
- `degraded -> disconnected` on persistent runtime loss
- `ready|degraded|disconnected -> stopped` on close
- `ready|degraded|disconnected -> faulted` only on close/shutdown fault

## Claim discipline
This contract is intentionally bounded to the current U6 proof slice. It does not claim broad hot-swap semantics or production-grade fault management beyond what the package proves.
