# Windows Path-Budget Compliance Note

## Purpose
This note records the delivery-shape correction made after the prior package produced a Windows extraction failure caused by long packaged paths and shipped cache artifacts.

## Controls added
- package builder still excludes `__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`, and `.ruff_cache`
- package builder now supports an explicit short `--delivery-root`
- package builder now validates candidate packaged paths against a representative Windows extraction root before zip creation
- local gate includes a Windows path-budget validation step

## Validation used in this pass
Command:

```text
python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root udq_s02b_r01
```

Result:
- PASS

## Delivery guidance for this pass
Use a short delivery root in the final zip, for example:
- `udq_s02b_r01`

Keep the full governed package identity in the manifest, release notes, and review-entry documents rather than in the outer filesystem root.
