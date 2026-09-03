# AGENTS.md

## Repository purpose

`mirops-compat` is the source-of-truth compatibility catalog for Kubernetes add-ons used by
Mirops. Each add-on maps add-on version ranges to Kubernetes version ranges.

## Layout

- `addons/*.yaml`: hand-curated, one file per add-on; edit these in pull requests.
- `schema/addon.schema.json`: per-file JSON Schema.
- `scripts/`: deterministic catalog validation and matrix generation helpers.
- `kubernetes/deprecated-apis.yaml`: generated Kubernetes API deprecation data.
- `.github/workflows/`: pull-request validation and OCI release workflows.
- `dist/`: generated output; never edit or commit it.

## Add-on data rules

- Use a lowercase kebab-case `name` matching the filename without `.yaml`.
- Use the project's official compatibility or support documentation as `source`.
- Set `lastVerified` to the month the source was checked (`YYYY-MM`).
- Keep ranges explicit and conservative. Do not invent an upper bound when the source does not
  provide one.
- `bestEffort` is allowed only for reproducible community-tested compatibility and must include an
  `evidence` URL on the rule. Official-source rows are preferred.
- Keep archived projects only for compatibility with existing users and document their status in
  a YAML comment or the source documentation.
- Do not duplicate an add-on under another filename or add overlapping rules for the same version.

## Validation and build

From the repository root:

```sh
make validate
make build
```

`make validate` runs the JSON Schema check and cross-file integrity checks. `make build` creates
the generated `dist/matrix.yaml`; CI performs the same validation before publishing the OCI
artifact. If `make` is unavailable, run the commands documented in `Makefile` directly.

## Change workflow

1. Update or add the relevant `addons/<name>.yaml` file.
2. Verify every rule against its official `source`.
3. Run `make validate` and `make build`.
4. Inspect the generated matrix and the diff for unrelated changes.
5. Do not edit `dist/` or generated Kubernetes deprecation data by hand.

Preserve unrelated worktree changes. Avoid destructive commands such as hard resets or broad
deletions. Keep pull requests focused and explain any compatibility inference.

## Review checklist

- Filename, `name`, and `displayName` are correct.
- Source URL is official and reachable.
- Verification month is current.
- Every rule has a meaningful add-on range and Kubernetes range.
- Rules do not overlap or contradict each other.
- Validation and matrix generation pass.
- Documentation and CI changes match the actual repository commands.
