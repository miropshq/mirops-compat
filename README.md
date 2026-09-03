# mirops-compat

The **Kubernetes add-on compatibility library** for [mirops](https://github.com/miropshq/mirops) —
which add-on versions run on which Kubernetes versions, community-maintained and vendor-verified.
Think *endoflife.date, but a cross–add-on compatibility matrix.*

The mirops operator uses this to decide whether an upgrade is safe. This repo is the **source of
truth**; the operator ships an embedded snapshot, and the Helm chart can pull a chosen published
version into an override ConfigMap — so you can update the matrix without a new operator release.

---

## Layout

```
addons/*.yaml            # one file per add-on — hand-curated, vendor-verified (edit by PR)
kubernetes/
  deprecated-apis.yaml   # deprecated/removed APIs — GENERATED from upstream, not hand-edited
schema/addon.schema.json # validates every addons/*.yaml in CI
.github/workflows/       # validation and OCI release workflows
scripts/                 # cross-file validation and matrix generation
.github/workflows/
  release.yml            # schema-checks, merges addons/*.yaml → dist/matrix.yaml, pushes to GHCR
dist/matrix.yaml         # generated artifact (embedded by the operator + published to OCI)
```

## How it's consumed (two layers, override wins)

```
1. ConfigMap  mirops-compatibility-matrix  → the operator reads this as an override. Populate it by
                                             pulling a published OCI version with the Helm chart
                                             (compatMatrix.enabled=true), or ship your own add-on rules.
2. Embedded   internal/compat/matrix.yaml  → snapshot baked into the operator — the default, always
                                             present (offline / air-gapped safe).
```

The operator uses the **embedded** matrix unless the override ConfigMap is present. The **OCI artifact
published here is the source the Helm chart pulls into that ConfigMap** — the operator itself never
reaches a registry at runtime, so it always starts, even air-gapped or when GHCR is down.

Versions are tagged by **UTC date** (`vYYYY.MM.DD`), plus a moving **`latest`** tag. Pin a date for
reproducible upgrade verdicts in production; use `latest` to stay current in non-prod.

## Inspecting what a published version covers

Compatibility isn't defined per OCI tag — it's defined per add-on in [`addons/*.yaml`](addons/)
(the `rules:` mapping `addonRange` → `k8sRange`). Each published tag is just a **frozen snapshot** of
all those rules at that date, merged into a single `matrix.yaml`. To see exactly what a tag covers,
pull it and read the file — there is no separate index:

```sh
# a pinned date
oras pull ghcr.io/miropshq/mirops-compat:v2026.08.30 --output ./matrix
cat ./matrix/dist/matrix.yaml     # every add-on and its addonRange → k8sRange rules

# or the moving 'latest'
oras pull ghcr.io/miropshq/mirops-compat:latest --output ./matrix
cat ./matrix/dist/matrix.yaml
```

If it's already running in a cluster, read the same content from the override ConfigMap the operator
consumes (when `compatMatrix.enabled=true` populated it):

```sh
kubectl get configmap mirops-compatibility-matrix -n mirops -o jsonpath='{.data.matrix\.yaml}'
```

When that ConfigMap isn't present the operator uses its **embedded** snapshot (baked into the image
at build), which tracks the operator's own release rather than a date tag.

## Release flow

```
PR to addons/*.yaml → CI validates against schema → merge
  → CI merges addons/*.yaml → dist/matrix.yaml
  → CI runs oras push ghcr.io/miropshq/mirops-compat:vYYYY.MM.DD  (tag = UTC date) + retags 'latest'
  → the Helm chart can pull that version into the override ConfigMap; the operator re-embeds the
    snapshot on its next release
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
    bestEffort: true            # community-tested, not vendor-supported
    evidence: https://example.org/test-report
```

## Local checks

```sh
make validate  # schema-check and enforce catalog-wide invariants
make build     # generate dist/matrix.yaml
make clean     # remove generated matrix
```

`make validate` requires Python with PyYAML and the `check-jsonschema` command. The catalog-wide
checks enforce filename/name consistency, unique IDs, verification-date format, required metadata,
nonempty rules, and non-overlapping add-on ranges.

The catalog covers widely deployed upstream, CNCF, Kubernetes SIG, and major cloud-provider
add-ons. Compatibility rows are based on official project documentation; unverifiable extrapolated
rows should not be added.

Building and publishing `dist/matrix.yaml` happens only in
[`.github/workflows/release.yml`](.github/workflows/release.yml) — there is no local publish path.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Every rule must trace to an official `source`; unverified
rules without vendor confirmation must be marked `bestEffort: true` and include community evidence. License: Apache-2.0.
