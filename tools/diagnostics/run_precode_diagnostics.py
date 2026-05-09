from __future__ import annotations

import argparse
from pathlib import Path

from tools._registry_paths import active_registry_path
from tools._shared import load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    gov = load_json(active_registry_path(root, 'governance_model_json'))
    print(f"precode-diagnostics: package_id={gov['package_id']} disposition={gov['package_disposition']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
