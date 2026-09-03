#!/usr/bin/env python3
"""Validate catalog-wide invariants not expressible in the per-file JSON Schema."""
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required (install check-jsonschema or PyYAML)") from exc

ROOT = Path(__file__).resolve().parents[1]
ADDONS = ROOT / "addons"
DATE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CONSTRAINT = re.compile(r"(>=|<=|>|<|=)?\s*(\d+)\.(\d+)\.(\d+)")
errors = []
seen = {}
allowed_addon = {"name", "displayName", "source", "lastVerified", "rules"}
allowed_rule = {"addonRange", "k8sRange", "bestEffort", "evidence"}

for path in sorted(ADDONS.glob("*.yaml")):
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: YAML parse failed: {exc}")
        continue
    if not isinstance(data, dict):
        errors.append(f"{path.name}: document must be an object")
        continue
    unknown = set(data) - allowed_addon
    if unknown:
        errors.append(f"{path.name}: unknown fields: {', '.join(sorted(unknown))}")
    name = data.get("name")
    if not isinstance(name, str) or not NAME.fullmatch(name):
        errors.append(f"{path.name}: invalid name")
        continue
    if path.stem != name:
        errors.append(f"{path.name}: filename must match name {name!r}")
    if name in seen:
        errors.append(f"duplicate addon name {name!r}: {seen[name]} and {path.name}")
    seen[name] = path.name
    if not isinstance(data.get("displayName"), str) or not data["displayName"].strip():
        errors.append(f"{path.name}: displayName is required")
    if not isinstance(data.get("source"), str) or not data["source"].startswith(("https://", "http://")):
        errors.append(f"{path.name}: source must be an HTTP(S) URL")
    if not isinstance(data.get("lastVerified"), str) or not DATE.fullmatch(data["lastVerified"]):
        errors.append(f"{path.name}: lastVerified must use YYYY-MM")
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        errors.append(f"{path.name}: rules must be a nonempty list")
        continue
    intervals = []
    for index, rule in enumerate(rules, 1):
        if not isinstance(rule, dict):
            errors.append(f"{path.name}: rule {index} must be an object")
            continue
        unknown_rule = set(rule) - allowed_rule
        if unknown_rule:
            errors.append(f"{path.name}: rule {index} unknown fields: {', '.join(sorted(unknown_rule))}")
        if not isinstance(rule, dict) or not isinstance(rule.get("addonRange"), str) or not rule["addonRange"].strip():
            errors.append(f"{path.name}: rule {index} has no addonRange")
        if not isinstance(rule, dict) or not isinstance(rule.get("k8sRange"), str) or not rule["k8sRange"].strip():
            errors.append(f"{path.name}: rule {index} has no k8sRange")
            continue
        if "bestEffort" in rule and not isinstance(rule["bestEffort"], bool):
            errors.append(f"{path.name}: rule {index} bestEffort must be boolean")
        if rule.get("bestEffort") is True:
            if not isinstance(rule.get("evidence"), str) or not rule["evidence"].startswith(("https://", "http://")):
                errors.append(f"{path.name}: rule {index} bestEffort requires an evidence URL")
        elif "evidence" in rule:
            errors.append(f"{path.name}: rule {index} evidence is only valid with bestEffort: true")
        lower = (0, 0, 0)
        upper = None
        for operator, major, minor, patch in CONSTRAINT.findall(rule["addonRange"]):
            version = (int(major), int(minor), int(patch))
            if operator in (">=", ">", "="):
                lower = max(lower, version)
            elif operator in ("<", "<="):
                candidate = version if operator == "<" else (version[0], version[1], version[2] + 1)
                upper = candidate if upper is None else min(upper, candidate)
        intervals.append((index, lower, upper))
    for left_index, left_lower, left_upper in intervals:
        for right_index, right_lower, right_upper in intervals:
            if right_index <= left_index:
                continue
            if (left_upper is None or right_lower < left_upper) and (right_upper is None or left_lower < right_upper):
                errors.append(f"{path.name}: addon rules {left_index} and {right_index} overlap")

if errors:
    print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
    raise SystemExit(1)
print(f"validated {len(seen)} addon files")
