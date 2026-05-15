@echo off
setlocal
set ROOT=%~dp0\..\..
set OUTPUT_DIR=proof/field_tests
set COMMON_ARGS=--package-root "%ROOT%" --output-dir "%OUTPUT_DIR%"
if exist "%ROOT%\.venv\Scripts\python.exe" (
  "%ROOT%\.venv\Scripts\python.exe" -m tools.diagnostics.run_u6_direct_open_probe %COMMON_ARGS% %*
) else (
  python -m tools.diagnostics.run_u6_direct_open_probe %COMMON_ARGS% %*
)
