# Contributing

Thanks for keeping the matrix accurate. It gates real upgrades, so **every rule must trace to an
official source.**

## Add or update an add-on

1. Edit (or add) `addons/<name>.yaml`. One file per add-on — this keeps PRs conflict-free.
2. Fill the fields:
   - `name` — kebab-case id, must match what the mirops collector detects.
   - `source` — **required**. The official vendor support/compatibility table you took the ranges from.
   - `lastVerified` — `YYYY-MM` when you confirmed the ranges against `source`.
   - `rules` — `addonRange` (the add-on versions) → `k8sRange` (the Kubernetes versions they support).
     Ranges use blang/semver syntax (`>=1.30.0 <1.31.0`, `>=1.32.0 <=1.36.0`).
3. Mark any rule you **could not** confirm against `source` with `bestEffort: true`.
4. Run locally:
   ```sh
   make validate   # schema-check
   ```
5. Open a PR. CI validates the schema and builds the merged matrix. A maintainer confirms the
   `source`.

## Rules of thumb

- **Cite the vendor, not a blog.** `source` should be the project's own support page.
- **Don't invent ranges.** If unsure, mark `bestEffort: true` and say so in the PR.
- **Keep ranges tight.** Prefer explicit minor bounds over open-ended `>=` where the vendor gives them.
- **Removed add-ons** (archived/EOL projects) can stay with a note in the PR; users still run them.

## Releasing (maintainers)

Merging to `main` is the release. CI builds `dist/matrix.yaml` and publishes the OCI artifact
to `ghcr.io/miropshq/mirops-compat:vYYYY.MM.DD`, where the tag is the **UTC date of the upload** —
two releases on the same day overwrite the same tag. Bump the operator's embedded snapshot / default
`ociRef` to adopt it.
