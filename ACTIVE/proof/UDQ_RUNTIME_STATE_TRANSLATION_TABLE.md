# UniversalDAQ — Runtime State Translation Table

| Source token | Normalized family | Reviewer label |
|---|---|---|
| `ready_to_configure` | `configuration_pre_run` | pre-run / configure |
| `configured` | `configuration_pre_run` | pre-run / configure |
| `live` | `live_ready_healthy` | live / ready / healthy |
| `ready` | `live_ready_healthy` | live / ready / healthy |
| `degraded` | `degraded` | degraded |
| `disconnected` | `disconnected` | disconnected |
| `recovering` | `recovering` | recovering |
| `faulted` | `faulted` | faulted |
| `stopped` | `stopped` | stopped |
