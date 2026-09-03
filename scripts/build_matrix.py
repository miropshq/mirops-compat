#!/usr/bin/env python3
"""Build the flat matrix consumed by the operator."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
addons = {}
for path in sorted((ROOT / "addons").glob("*.yaml")):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    addons[data["name"]] = [
        {"addonRange": rule["addonRange"], "k8sRange": rule["k8sRange"]}
        for rule in data["rules"]
    ]

out = ROOT / "dist" / "matrix.yaml"
out.parent.mkdir(exist_ok=True)
out.write_text(
    "# GENERATED — do not edit. Source of truth: addons/*.yaml\n"
    + yaml.safe_dump({"addons": addons}, sort_keys=False),
    encoding="utf-8",
)
print(f"built {len(addons)} addons into {out}")
