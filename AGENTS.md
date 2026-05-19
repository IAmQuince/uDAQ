## Cursor Cloud specific instructions

### Project overview

UniversalDAQ (uDAQ) is a pure Python (>=3.11) data acquisition platform. No external services, databases, Docker, or web servers are required. All code lives under `ACTIVE/`.

### Working directory

All commands must be run from `/workspace/ACTIVE` (where `pyproject.toml` lives), not the repo root.

### Installing dependencies

```
cd /workspace/ACTIVE
pip install -e ".[dev]"
```

The `[dev]` extra installs pytest, ruff, mypy, and pre-commit. The `[ui]` extra adds PySide6/pyqtgraph (not needed in headless environments).

### Running tests

```
python3 -m pytest tests/ -q
```

265 tests pass. 10 meta/governance tests fail due to pre-existing issues (cache artifacts in root, root-layer allowlist drift, etc.) — these are not caused by environment setup.

### Linting

```
python3 -m ruff check src/ tests/ tools/
python3 -m ruff format --check src/ tests/ tools/
python3 -m mypy src/universaldaq/ --ignore-missing-imports
```

Pre-existing lint/type errors exist in the repo (518 ruff, 295 mypy). These are known.

### CI quality gate

```
python3 -m tools.dev.run_local_gate --package-root .
```

This runs governance validators, shell smoke, ruff, ruff-format, mypy, and pytest sequentially. It will fail on the pre-existing lint issues when `--strict-dev-tools` is passed. Without that flag it skips missing tools gracefully.

### Smoke tests

```
python3 -m tools.dev.run_shell_smoke --package-root .
python3 -m tools.dev.run_labjack_u6_smoke --package-root .
```

Both run in simulated mode (no hardware needed).

### Key gotcha: PATH for installed scripts

After `pip install -e ".[dev]"`, console scripts (e.g. `pytest`, `ruff`, `mypy`) are placed in `~/.local/bin`. Ensure this is on `PATH`:

```
export PATH="$HOME/.local/bin:$PATH"
```

### Contributing

See `ACTIVE/CONTRIBUTING.md` and `ACTIVE/README.md` for the contributor flow and PR expectations.
