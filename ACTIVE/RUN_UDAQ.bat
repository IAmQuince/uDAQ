@echo off
setlocal
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1
python -m tools.ui.launch_operator_shell
if errorlevel 1 (
  echo.
  echo The visible shell did not launch successfully. Try RUN_DIAGNOSTICS.bat to create a report.
  pause
)
