# UDQ U6 State Transition Table

| From | Trigger | To | Visible consequence |
|---|---|---|---|
| configured | first poll starts backend init | initializing | startup in progress |
| initializing | backend init succeeds | ready | real device path healthy |
| initializing | backend init fails | disconnected | startup unavailable / reconnect failed |
| ready | first runtime read failure | degraded | bounded warning state |
| degraded | next startup/read succeeds | ready | bounded recovery observed |
| degraded | persistent runtime loss or failed reconnect | disconnected | device-loss state |
| ready/degraded/disconnected | close | stopped | adapter closed |
| any active state | close fault | faulted | shutdown fault recorded |
