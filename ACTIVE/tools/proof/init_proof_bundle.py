from __future__ import annotations

import argparse, json
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="UDQ-EXM-001")
    args = parser.parse_args()
    path = Path("proof/bundles") / f"{args.scenario.lower()}_bundle.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {"proof_id": f"PROOF-{args.scenario}", "scenario": args.scenario, "execution_contract_hash": "TBD", "proves_requirements": [], "generated_by": "tools/proof/init_proof_bundle.py"}
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print(path)
