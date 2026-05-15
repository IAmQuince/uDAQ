@echo off
setlocal
set ROOT=%~dp0..\..
set OUTPUT_DIR=proof/field_tests
set COMMON_ARGS=--package-root "%ROOT%" --output-dir "%OUTPUT_DIR%" --real-hardware --stabilization-cycles 6 --real-cycle-delay-seconds 0.75 --reconnect-settle-seconds 2.0
if exist "%ROOT%\.venv\Scripts\python.exe" (
  "%ROOT%\.venv\Scripts\python.exe" -m tools.dev.run_u6_field_test_harness %COMMON_ARGS% %*
) else (
  python -m tools.dev.run_u6_field_test_harness %COMMON_ARGS% %*
)
