# CUBI — Invariant 124 baseline freeze

State: LOCKED BASELINE (append-only governance)
Freeze date: 2026-10-31
Current baseline: 124
Next permissible experimental extension: 125
Original snapshot: invariants/124/index.html
Verified original Git blob SHA-1: 71bc1332216008b870017ac16b8f85a308f5751e
Verified: same original blob in DavidWise01/cubi and DavidWise01/DavidWise01.github.io.
Original source commits recorded at publication:
- cubi: f8943f2ff04f
- GitHub Pages: 27fdb764389c

## Canonical model
Torsional toy oscillator: theta'' + gamma theta' + theta = u.
E = (theta^2 + theta'^2)/2.
u = clip((gamma + g(E_target - E)) theta', -u_max, +u_max).
gamma=0.2; g=0.8; E_target=0.5; u_max=0.4.

## Fixed observed evidence
Spacing: 13.780 model time units.
Phase samples: 512; independent sign patterns: 3.
Observed minimum sustained hold: 8.0041889506.
Required hold: 8.0.
Observed surplus: 0.0041889506.
Half phase-gap: 0.006135923151542565 radians.
Maximum adjacent envelope finite-difference slope: 47.914742022329264 time units/radian.
Coarse/fine maximum difference: 0.000024662390000429468.
Sufficient global Lipschitz cap under an **unproven** assumption that the integration error is at most that difference: 0.6786734623546187.
Heuristic substituted lower estimate: 7.710163113335; **NOT A CERTIFIED LOWER BOUND**.

A: sampled hold evidence PASS.
B: phase sensitivity CHECK.
C: rigorous all-phase certification OPEN.
No global Lipschitz bound, rigorous integration error enclosure, or all-phase guarantee has been proved.
No physical spinor claim.

## Ownership and preservation
This file declares an append-only canonical baseline. Future work must be in new invariant directories and preserve invariant 124 unchanged; corrections are recorded separately as errata or superseding versions. Git commits and blob hashes make unauthorized drift detectable, but GitHub remains technically editable by administrators. This is a project governance lock, not a cryptographic immutability guarantee.

## Three independent witnesses
A: sampled recovery evidence, B: sensitivity and numerical discrepancy, C: certification status. Witnesses report, not vote or form quorum.

## ASCII
```
. | . | . | . | . | . | .
. | INVARIANT 124 LOCKED  |
. | JACOBI :: |-|-|-|    |
. | JOSOPHENE j/`-`\\j  |
. | JULIET :: -+i^2     |
. | A:PASS B:CHECK C:OPEN|
. |          {{i}}        |
. | NEXT: 125 APPEND-ONLY|
. | . | . | . | . | . | .
```
