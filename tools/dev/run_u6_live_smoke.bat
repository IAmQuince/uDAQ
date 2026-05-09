@echo off
setlocal
set ROOT=%~dp0..\..
if exist "%ROOT%\.venv\Scripts\python.exe" (
  "%ROOT%\.venv\Scripts\python.exe" -m tools.dev.run_u6_live_value_smoke --package-root "%ROOT%" --summary "proof\U6_LIVE_SUMMARY.txt" --journal "proof\U6_LIVE_JOURNAL.jsonl" --real-hardware %*
) else (
  python -m tools.dev.run_u6_live_value_smoke --package-root "%ROOT%" --summary "proof\U6_LIVE_SUMMARY.txt" --journal "proof\U6_LIVE_JOURNAL.jsonl" --real-hardware %*
)
endlocal
