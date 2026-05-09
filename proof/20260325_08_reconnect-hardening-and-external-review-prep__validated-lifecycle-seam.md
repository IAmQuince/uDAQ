# 20260325_08 validated lifecycle seam

## Purpose
This note captures the canonical lifecycle seam now validated by the current real-hardware specimen lane. It is written in main-app terms so future device lanes can inherit the same contract.

## Canonical seam
1. **discover/select active adapter**
2. **startup open/init**
3. **first healthy sample**
4. **live operation**
5. **device loss observed**
6. **recovering**
7. **recovered**
8. **stabilized**

## Stage definitions

### 1. discover/select active adapter
The app identifies one candidate adapter for the active run and binds the session to that adapter identity.

Evidence surfaces:
- preflight report
- active adapter id in diagnostics
- discovery strategy note when present

Exit condition:
- one active adapter is selected for startup/open.

### 2. startup open/init
The app attempts the first real open/init on the selected adapter.

Evidence surfaces:
- startup-open counters and classification
- startup/open runtime evidence where retained
- direct-open probe result when used as a bounded preflight discriminator

Exit condition:
- the adapter is opened and initialized sufficiently to attempt a first healthy sample.

### 3. first healthy sample
The app proves the adapter is not merely open, but capable of producing a healthy first sample/read.

Evidence surfaces:
- startup-open success counters
- baseline phase results
- review summary / smoke summary final baseline posture

Exit condition:
- baseline posture reaches `live / ready / healthy`.

### 4. live operation
The app is actively operating with a healthy adapter.

Evidence surfaces:
- lifecycle summary phase `live`
- adapter state `ready`
- reviewer label `live / ready / healthy`

Exit condition:
- session remains healthy until a bounded stop or a real device-loss incident occurs.

### 5. device loss observed
A live session loses its active adapter and the app records that loss as a real runtime incident.

Evidence surfaces:
- disconnect count increase
- disconnect-class runtime evidence
- device-loss phase record
- reviewer label/state family shifting away from healthy live posture

Exit condition:
- the session is definitively in a disconnected/degraded posture.

### 6. recovering
The app begins bounded reacquire/reopen work after device loss.

Evidence surfaces:
- reconnect attempt counters
- reconnect strategy plan/trace
- recovery-window phase record

Exit condition:
- a fresh open path is attempted and the app advances to a first successful post-loss read, or recovery fails for that attempt.

### 7. recovered
The adapter has been reacquired, reopened, and verified with a successful first post-loss read.

Evidence surfaces:
- recovery count increase
- successful post-disconnect poll
- adapter rebound observation
- `device_recovered` runtime evidence where retained

Exit condition:
- the session returns to ready/live posture.

### 8. stabilized
Recovered state remains healthy for the bounded stabilization window.

Evidence surfaces:
- post-recovery stabilization phase `PASS`
- final reviewer label `live / ready / healthy`
- final state family `live_ready_healthy`

Exit condition:
- the lane is accepted as recovered and stable for the bounded run.

## Why this seam matters
The lane now proves that startup/open and reconnect/recovery should be treated as one app-owned lifecycle contract with different entry points, not as disconnected device-specific stories.

## Current specimen posture
The current LabJack U6 lane is the first full real-hardware specimen that validates this seam end-to-end. That does not generalize all future hardware lanes automatically, but it does provide the template future lanes should inherit.
