# UniversalDAQ — Runtime Metric Dictionary

## Reviewer layer
- reviewer label
- normalized state family
- active alarm count
- unacknowledged alarm count
- disconnect count
- recovery count
- recent runtime-event count
- recent operator-action count
- needs-review flag

## Engineering layer
- queue depths/drops
- presentation publish/coalesce counts
- recent sample/cycle/variable-transition counts
- journal writes/flushes/drops
- adapter consecutive failures/reconnect attempts

## Internal layer
Selected raw `runtime.*` and `commands.*` counters, timings, and gauges from `RuntimeMetricsStore`.
