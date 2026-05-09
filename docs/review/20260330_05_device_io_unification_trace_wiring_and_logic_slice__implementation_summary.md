# 20260330_05 Device I/O Unification, Trace Wiring, and Logic Slice

This pass is the last focused implementation run before the documentation reconciliation pass. It consolidates device-centered inspection and canonical tagging in the System workspace, makes the top information bar informative at a glance with stable semantic colors, turns a richer subset of trace-style controls into visible plot changes, gives PiP an obvious top-bar recovery path, and advances Logic Designer from a static placeholder toward a draft/simulated executable slice.

The implementation remains intentionally careful about authority: backend-applied bindings remain separate from shell draft state, and the new Device I/O Inspector is a canonical inspection and naming surface rather than an applied runtime mutation path.
