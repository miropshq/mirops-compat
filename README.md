# mirops-compat

The **Kubernetes add-on compatibility library** for [mirops](https://github.com/miropshq/mirops) —
which add-on versions run on which Kubernetes versions, community-maintained and vendor-verified.
Think *endoflife.date, but a cross–add-on compatibility matrix.*

The mirops operator uses this to decide whether an upgrade is safe. This repo is the **source of
truth**; the operator ships an embedded snapshot and can also pull a pinned version at runtime.

---

## Layout

```
addons/*.yaml            # one file per add-on — hand-curated, vendor-verified (edit by PR)
kubernetes/
  deprecated-apis.yaml   # deprecated/removed APIs — GENERATED from upstream, not hand-edited
schema/addon.schema.json # validates every addons/*.yaml in CI
scripts/
  build.sh               # merges addons/*.yaml → dist/matrix.yaml (the operator's shape)
  publish.sh             # pushes dist/matrix.yaml to GHCR as an OCI artifact
dist/matrix.yaml         # generated artifact (embedded by the operator + published to OCI)
```

## How it's consumed (three layers, highest wins)

```
1. ConfigMap  mirops-compatibility-matrix   → per-cluster overrides (the user's own add-ons)
2. OCI        ghcr.io/miropshq/compat:vX     → pinned version, pulled at startup (update without
                                                a new operator release)
3. Embedded   internal/compat/matrix.yaml    → snapshot baked into the operator (offline fallback,
                                                always present — air-gapped safe)
```

The operator tries the OCI pull, then **falls back to the embedded snapshot** on any failure, so it
always starts — even air-gapped or when GHCR is down.

## Release flow

```
PR to addons/*.yaml → CI validates against schema → merge → tag vYYYY.MM.DD
  → CI runs build.sh → dist/matrix.yaml
  → CI runs publish.sh → oras push ghcr.io/miropshq/compat:vYYYY.MM.DD
  → operator bumps its embedded snapshot and/or its default ociRef
```

## Add-on file format (`addons/istio.yaml`)

```yaml
name: istio                 # kebab-case id (matches the add-on the collector detects)
displayName: Istio
source: https://istio.io/latest/docs/releases/supported-releases/   # required — the vendor table
lastVerified: "2026-06"     # when the ranges were confirmed against `source`
rules:
  - addonRange: ">=1.30.0"      # semver range (blang/semver); an add-on version satisfying this…
    k8sRange: ">=1.32.0 <=1.36.0" # …is supported on these Kubernetes versions
  - addonRange: ">=1.26.0 <1.27.0"
    k8sRange: ">=1.29.0 <=1.33.0"
    bestEffort: true            # extrapolated, not vendor-confirmed — confirm before relying on it
```

## Build & publish

```sh
make build     # addons/*.yaml → dist/matrix.yaml   (needs yq v4)
make validate  # schema-check every addons/*.yaml
make publish   # oras push dist/matrix.yaml → GHCR   (needs oras + a tag)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Every rule must trace to an official `source`; unverified
rules are marked `bestEffort: true`. License: Apache-2.0.
