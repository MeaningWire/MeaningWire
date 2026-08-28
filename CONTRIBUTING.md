# Contributing to MeaningWire

Thank you for considering a contribution. MeaningWire is intentionally being built in public, and careful disagreement is welcome.

## Good first contributions

Useful early contributions include:

- documentation corrections and examples;
- terminology and semantic-model critiques;
- standards crosswalk research;
- accessibility improvements;
- deterministic tests;
- schema and mapping edge cases;
- adapter design feedback;
- reproducible bug reports.

## Before opening a large pull request

For changes to canonical schemas, mapping semantics, identifiers, event contracts, provenance, authority rules, adapter interfaces, or governance, open an issue or RFC first. Large semantic changes are easier to review when the problem and alternatives are discussed before implementation.

## Contribution workflow

1. Fork or branch from the current default branch.
2. Keep each change focused.
3. Add or update tests for behavior changes.
4. Update documentation when public behavior changes.
5. Explain compatibility, provenance, and authority effects where relevant.
6. Open a pull request with enough context for an unfamiliar reviewer to evaluate it.

## Pull request expectations

A strong pull request answers:

- What problem does this solve?
- Why is this approach preferable?
- What public contracts change?
- Is the change backward compatible?
- Does it introduce lossy transformation?
- What provenance is preserved or altered?
- Does it change any human or system authority boundary?
- How was it tested?
- What maturity state should the result have?

Not every question applies to every change, but semantic and interoperability changes should address them explicitly.

## Vendor neutrality

Do not optimize a public contract around a private or proprietary downstream implementation unless the abstraction also makes sense independently.

Vendor-specific adapters are welcome when they terminate at public MeaningWire contracts and do not quietly redefine the canonical model around that vendor.

## AI-assisted contributions

AI tools may be used, but the contributor remains responsible for correctness, licensing, security, provenance, and the factual accuracy of any claims. AI-generated interpretation must not be presented as human approval or expert validation.

## Standards and external material

When mapping external standards:

- cite the relevant specification or source;
- distinguish normative requirements from project interpretation;
- do not copy restricted material into the repository without permission;
- record known loss, ambiguity, or unsupported concepts.

## Accessibility

Documentation and user-facing interfaces should target WCAG 2.2 AA. Prefer clear language, predictable navigation, progressive disclosure, and low-cognitive-load defaults.

## Conduct

Participation is subject to [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Do not open public issues for suspected vulnerabilities that could put users at risk. Follow [SECURITY.md](SECURITY.md).

## License status

The project license has not yet been finalized. Contributions should not be submitted with assumptions about downstream reuse rights until the repository contains an explicit license and contribution policy aligned to it.
