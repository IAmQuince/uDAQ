@echo off
setlocal
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1
python -m tools.dev.run_sprint_diagnostics --package-root .
echo.
echo Diagnostics completed. Review ACTIVE\diagnostics\20260515_02_diagnostic-bundle.zip if present.
pause
