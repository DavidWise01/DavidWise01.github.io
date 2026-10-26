# FORMIC v1.2 — Source Freeze

Frozen on 2026-10-26. Canonical boundary: **FORMIC_IN → witnesses → HEGEMON → bounded advisory feedback → FORMIC_OUT**.

## Scope
Public GitHub repository and Pages metadata monitoring only. No intrusion claims, packet interception, automated firewall rules, auto-repair, or repository mutations by the defensive policy. The scheduled evidence publisher may commit observations to this same repository.

## Baseline
- Last functional dashboard update: `9df3e21c201429ad45c547b67eaca1e1539f9f73`
- Synthetic freeze test commit: `375ab43bcb687378c4ea1a94635d5b9e1e9f2bc5`
- Workflow CI gate commit: `50db13e1fc0632adf43d07bf492391cc919407a2`
- Observer cadence: hourly GitHub Actions at minute 17, subject to GitHub scheduler delay.
- Hash chain: SHA-256 of canonical diodic frame, not a signature or external attestation.
- Feedback: 3 observed review cycles for sustained review; 2 clear cycles for recovery.
- Witnesses: A inventory / B continuity / C provenance; independent reports, no voting.

## Verification ledger
- PASS: GitHub connector retrieved current Python modules, HTML dashboards, and scheduled workflow.
- PASS: Freeze invariants expressed as synthetic unit tests; workflow configured to run compileall and tests before observation.
- NOT YET VERIFIED: successful GitHub Actions run of new tests and observers.
- NOT YET VERIFIED: external website availability from the present checking environment.
- NOT YET VERIFIED: persistent files `formic/status.json` and `formic/arcade.json` (both were absent when checked).
- NO SECURITY FINDING: lack of monitoring snapshots or unavailable external reachability checks does not prove an outage or intrusion.

## Change control
This file records a *source baseline*, not a Git branch protection setting, immutable Git tag, validated deployment, or proof that production monitoring is running. Later improvements should land as new versioned changes rather than silently rewriting this freeze record.

## End condition
**FORMIC_OUT** records an advisory result, no automatic execution, and the digest for the next **FORMIC_IN**.
