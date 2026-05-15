@echo off
setlocal
set ROOT=%~dp0..\..
if exist "%ROOT%\.venv\Scripts\python.exe" (
  "%ROOT%\.venv\Scripts\python.exe" -m tools.dev.run_u6_diag --package-root "%ROOT%" --out "proof\U6_DIAG.txt" --real-hardware %*
) else (
  python -m tools.dev.run_u6_diag --package-root "%ROOT%" --out "proof\U6_DIAG.txt" --real-hardware %*
)
endlocal
