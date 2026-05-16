from __future__ import annotations

from pathlib import Path

from .state import (
    RuntimeStateSnapshot,
    build_authoritative_runtime_snapshot as _build_authoritative_runtime_snapshot,
)


def get_authoritative_runtime_state_snapshot(*, package_root: Path | str | None = None) -> RuntimeStateSnapshot:
    _ = package_root
    return _build_authoritative_runtime_snapshot()


def get_runtime_state_snapshot(*, package_root: Path | str | None = None) -> RuntimeStateSnapshot:
    return get_authoritative_runtime_state_snapshot(package_root=package_root)


def build_authoritative_runtime_state_snapshot(*, package_root: Path | str | None = None) -> RuntimeStateSnapshot:
    return get_authoritative_runtime_state_snapshot(package_root=package_root)


def build_authoritative_runtime_snapshot(*, package_root: Path | str | None = None) -> RuntimeStateSnapshot:
    return get_authoritative_runtime_state_snapshot(package_root=package_root)


def build_runtime_state_snapshot(*, package_root: Path | str | None = None) -> RuntimeStateSnapshot:
    return get_authoritative_runtime_state_snapshot(package_root=package_root)


__all__ = [
    'RuntimeStateSnapshot',
    'build_authoritative_runtime_snapshot',
    'build_authoritative_runtime_state_snapshot',
    'build_runtime_state_snapshot',
    'get_authoritative_runtime_state_snapshot',
    'get_runtime_state_snapshot',
]
