from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, entry_points
from importlib.util import find_spec
from typing import Iterable
import pkgutil

from .models import SupportPackLoadReport, SupportPackLoadState, SupportPackProbeResult
from .services import AdapterManagerService

SUPPORT_PACK_ENTRY_POINT_GROUP = 'universaldaq.support_packs'
SUPPORT_PACK_NAMESPACE_PREFIX = 'universaldaq_'


def _root_package_name(module_name: str) -> str:
    return module_name.split('.', 1)[0]


def discover_optional_support_pack_modules() -> tuple[str, ...]:
    discovered: set[str] = set()
    try:
        eps = entry_points(group=SUPPORT_PACK_ENTRY_POINT_GROUP)
    except TypeError:  # pragma: no cover - compatibility fallback
        eps = entry_points().get(SUPPORT_PACK_ENTRY_POINT_GROUP, ())
    except PackageNotFoundError:  # pragma: no cover - defensive fallback
        eps = ()
    for entry_point in eps:
        raw_value = getattr(entry_point, 'value', '')
        module_name = raw_value.split(':', 1)[0] if isinstance(raw_value, str) else ''
        if module_name.endswith('.plugin'):
            discovered.add(module_name)
    for module_info in pkgutil.iter_modules():
        root_name = module_info.name
        if not root_name.startswith(SUPPORT_PACK_NAMESPACE_PREFIX) or root_name == 'universaldaq':
            continue
        plugin_module = f'{root_name}.plugin'
        try:
            if find_spec(plugin_module) is None:
                continue
        except ModuleNotFoundError:  # pragma: no cover - defensive fallback
            continue
        discovered.add(plugin_module)
    return tuple(sorted(discovered))


def load_optional_support_packs(
    adapters: AdapterManagerService,
    *,
    module_names: Iterable[str] | None = None,
) -> tuple[SupportPackLoadReport, ...]:
    reports: list[SupportPackLoadReport] = []
    resolved_module_names = tuple(module_names) if module_names is not None else discover_optional_support_pack_modules()
    for module_name in resolved_module_names:
        root_package = _root_package_name(module_name)
        try:
            if find_spec(root_package) is None:
                report = SupportPackLoadReport(
                    pack_id=root_package,
                    module_name=module_name,
                    state=SupportPackLoadState.MISSING,
                    summary='support pack package not installed',
                )
                adapters.record_support_pack_load_report(report)
                reports.append(report)
                continue
        except ModuleNotFoundError:
            report = SupportPackLoadReport(
                pack_id=root_package,
                module_name=module_name,
                state=SupportPackLoadState.MISSING,
                summary='support pack package not installed',
            )
            adapters.record_support_pack_load_report(report)
            reports.append(report)
            continue

        try:
            module = import_module(module_name)
        except Exception as exc:  # pragma: no cover - defensive path
            report = SupportPackLoadReport(
                pack_id=root_package,
                module_name=module_name,
                state=SupportPackLoadState.ERROR,
                summary=f'failed to import support pack module: {exc.__class__.__name__}',
                metadata={'exception': str(exc)},
            )
            adapters.record_support_pack_load_report(report)
            reports.append(report)
            continue

        probe = getattr(module, 'probe_support_pack', None)
        probe_result: SupportPackProbeResult | None = None
        if callable(probe):
            try:
                probe_result = probe()
            except Exception as exc:  # pragma: no cover - defensive path
                report = SupportPackLoadReport(
                    pack_id=root_package,
                    module_name=module_name,
                    state=SupportPackLoadState.ERROR,
                    summary=f'support pack probe failed: {exc.__class__.__name__}',
                    metadata={'exception': str(exc)},
                )
                adapters.record_support_pack_load_report(report)
                reports.append(report)
                continue
            if not probe_result.available:
                report = SupportPackLoadReport(
                    pack_id=probe_result.descriptor.pack_id,
                    module_name=module_name,
                    state=SupportPackLoadState.UNAVAILABLE,
                    summary=probe_result.summary,
                    metadata=dict(probe_result.metadata),
                )
                adapters.record_support_pack_load_report(report)
                reports.append(report)
                continue

        builder = getattr(module, 'build_support_pack_registration', None)
        if not callable(builder):
            report = SupportPackLoadReport(
                pack_id=root_package,
                module_name=module_name,
                state=SupportPackLoadState.ERROR,
                summary='support pack builder missing build_support_pack_registration',
            )
            adapters.record_support_pack_load_report(report)
            reports.append(report)
            continue

        try:
            registration = builder()
        except Exception as exc:  # pragma: no cover - defensive path
            report = SupportPackLoadReport(
                pack_id=(root_package if probe_result is None else probe_result.descriptor.pack_id),
                module_name=module_name,
                state=SupportPackLoadState.ERROR,
                summary=f'support pack builder failed: {exc.__class__.__name__}',
                metadata={'exception': str(exc)},
            )
            adapters.record_support_pack_load_report(report)
            reports.append(report)
            continue

        adapters.install_support_pack(registration)
        installed_report = SupportPackLoadReport(
            pack_id=registration.descriptor.pack_id,
            module_name=module_name,
            state=SupportPackLoadState.INSTALLED,
            summary='support pack installed',
            metadata={} if probe_result is None else dict(probe_result.metadata),
        )
        adapters.record_support_pack_load_report(installed_report)
        reports.append(installed_report)
    return tuple(reports)
