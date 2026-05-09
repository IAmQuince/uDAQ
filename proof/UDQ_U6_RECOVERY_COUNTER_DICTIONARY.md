# U6 Recovery Counter Dictionary

- `disconnect_count`: disconnect incidents, not reconnect attempts
- `reconnect_attempts`: reconnect attempts started after the first startup attempt
- `reconnect_backend_open_success_count`: successful backend reopen operations during reconnect handling
- `reconnect_backend_open_failure_count`: failed backend reopen operations during reconnect handling
- `post_disconnect_successful_poll_count`: successful polls observed after a disconnect incident had already opened
- `recovery_count`: recovery incidents closed successfully

## Important distinction
One disconnect incident may contain multiple reconnect attempts. A backend reopen is not the same as recovery. Recovery requires a post-disconnect successful poll.
