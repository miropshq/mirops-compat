# Security Policy

mirops-compat is a **data-only** repository — the community add-on ↔ Kubernetes compatibility matrix
consumed by the mirops operator. It ships no runtime code. We still appreciate responsible disclosure
for the build/publish pipeline and for the artifact it produces.

## Supported versions

The matrix is published under CalVer (`vYYYY.MM.DD`). Consumers should pin or track the **latest
published** matrix; older snapshots are not patched.

## Reporting a vulnerability

**Please do not open a public issue for security vulnerabilities.**

Report privately through either channel:

- **GitHub private vulnerability reporting** — *Security → Report a vulnerability* on the repository.
  This opens a private advisory visible only to the maintainers.
- **Email** — [security@mirops.com](mailto:security@mirops.com).

### What to expect

- **Acknowledgement** within a few business days.
- An assessment and, if confirmed, a fix timeline shared with you.
- Credit in the advisory once a fix is released, unless you prefer to remain anonymous.

## What is (and isn't) a security issue

- **Not** a security issue: inaccurate compatibility data (a wrong version range). That's a normal
  bug — open an issue or PR. Every add-on file is schema-validated in CI, and the operator treats the
  matrix as advice, not a secret.
- **Is** a security issue: a way to poison the published OCI artifact, bypass schema validation, or
  abuse the build/publish workflow (e.g. supply-chain or credential exposure in CI).

Thank you for helping keep mirops and its users safe.
