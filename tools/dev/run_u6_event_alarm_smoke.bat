@echo off
setlocal
set SCRIPT_DIR=%~dp0
set PACKAGE_ROOT=%SCRIPT_DIR%..\..
if exist "%PACKAGE_ROOT%\.venv\Scripts\python.exe" (
  set PYTHON_EXE=%PACKAGE_ROOT%\.venv\Scripts\python.exe
) else (
  set PYTHON_EXE=python
)
"%PYTHON_EXE%" -m tools.dev.run_u6_event_alarm_smoke --package-root "%PACKAGE_ROOT%" --summary "proof\U6_EVENT_ALARM_SUMMARY.txt" --journal "proof\U6_EVENT_ALARM_JOURNAL.jsonl" --real-hardware %*
exit /b %ERRORLEVEL%
