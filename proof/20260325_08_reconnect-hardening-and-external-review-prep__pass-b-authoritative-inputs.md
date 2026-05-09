# 20260325_08 reconnect hardening and external review prep — Pass B authoritative inputs

## Authoritative current proof inputs
These are the inputs Pass B treats as current truth for the validated real-hardware lane:

1. `proof/field_tests/20260325_04_real-u6-direct-open-probe`
   - proves the low-level real-hardware direct-open primitive on the current specimen lane
2. `proof/field_tests/20260325_01_real-u6-startup-open-smoke`
   - proves the startup/open → first healthy baseline seam
3. `proof/field_tests/20260325_02_real-u6-guided-unplug-replug-validation`
   - proves disconnect observation, reconnect, recovery, and stabilization on the current specimen lane
4. `proof/20260325_08_reconnect-hardening-and-external-review-prep__reconnect-churn-rca.md`
   - records the bounded Pass A interpretation of reconnect-attempt churn
5. `proof/20260325_08_reconnect-hardening-and-external-review-prep__startup-advisory-disposition.md`
   - records the Pass A disposition of the startup-smoke advisory
6. `proof/20260325_08_reconnect-hardening-and-external-review-prep__pass-a-hardening-summary.md`
   - summarizes the technical hardening outcome immediately preceding Pass B

## Historical but non-authoritative diagnostic inputs
These may still be consulted for context, but they are not the default review path:
- early startup-open failure bundles
- early guided reconnect-failure bundles
- Sprint 3B / 3C reference failure notes

## Pass B interpretation rule
Pass B builds doctrine from the current passing lane first. Historical failures are used only to explain why the current lifecycle seam and evidence model were shaped the way they are.
