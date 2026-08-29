# Canonical Domain Contract Conventions

MeaningWire domain contracts describe interoperable business meaning inside the `data` member of a MeaningWire envelope. They do not replace envelope identity, provenance, authority, or maturity metadata.

The first concrete domain contract is Identity / Party.

## Boundary rules

### Record identity belongs to the envelope

The canonical record identity is `envelope.record`. Domain data must not duplicate that identity as an invented `party_id`, `product_id`, or similar canonical field.

External or business identifiers are different: they belong in the domain payload as explicit scheme-aware identifiers because multiple source systems may know the same party by different identifiers.

### Unknown is omission, not an invented value

Optional fields are omitted when the source does not supply or justify them. The initial contracts do not use magic strings such as `unknown`, empty strings, or fabricated defaults to make records look complete.

### Contextual roles are not intrinsic identity

A party can be a buyer in one transaction, a supplier in another, an employer in another, and a message recipient elsewhere. Those roles belong to the relevant relationship, transaction, or event context rather than the intrinsic Party contract.

The initial Party schema therefore does not include fields such as `buyer`, `supplier_id`, or a universal `role`.

### Multiple names and identifiers are normal

Party data may contain multiple typed names and multiple identifiers. MeaningWire does not assume that one display name or one source-system identifier is globally authoritative.

### Contact points are explicit values

Contact information is represented as typed contact points. The first contract distinguishes `email`, `telephone`, `uri`, and `other` without imposing provider-specific field names or claiming that a syntactically shaped value has been operationally verified.

### Contracts remain closed by default

Experimental domain schemas currently use `additionalProperties: false`. New interoperable meaning should be added deliberately and versioned rather than entering silently through vendor-specific extension fields.

This does not prohibit future extension mechanisms; it prevents accidental extension from becoming an undeclared public contract.

## Identity / Party 0.1.0

The first Party contract deliberately covers only a small common denominator:

- party type: person, organization, group, or other;
- typed names;
- scheme-aware external/business identifiers;
- typed contact points.

A Party must contain at least one name, identifier, or contact point in addition to its type.

The schema deliberately does not yet model addresses, organizational hierarchy, party relationships, credentials, classifications, tax identity, financial accounts, lifecycle status, or transactional roles. Those require their own semantics rather than being added merely because another standard contains them.

## Standards research inputs

The design is informed by current public standards without copying any external model wholesale.

At the time of this experimental slice:

- OAGIS/connectSpec 10.12.8 documents Party Identifier as a scheme-aware party reference and Party Identifier Set as one-or-more identifiers with optional scheme, version, and agency metadata;
- OAGIS party/contact structures repeatedly compose identifiers, person names, addresses, communications, and contextual party references;
- Schema.org 30.0 models `Person` and `Organization` as distinct entity types and uses `contactPoint` / `ContactPoint` for contact information;
- Schema.org `Organization` also exposes identifiers such as ISO 6523 identifiers and GLNs, reinforcing that identifiers are properties of an entity rather than the entity model itself.

Reference pages:

- https://www.oagidocs.org/docs/party-identifier/
- https://www.oagidocs.org/docs/party-identifier-set/
- https://www.oagidocs.org/docs/application-party-reference/
- https://schema.org/Person
- https://schema.org/Organization
- https://schema.org/ContactPoint

MeaningWire intentionally does **not** reproduce the complete OAGIS Party model or Schema.org vocabulary. The purpose of standards research is to identify durable semantic common ground and explicit mapping points.

## Versioning direction

The current Party contract is `0.1.0` and `EXPERIMENTAL`. Breaking semantic changes are allowed during pre-release work but must remain explicit in schema IDs, registry entries, fixtures, mappings, and documentation.

Before a domain contract can be promoted beyond experimental maturity, it should have representative crosswalks, compatibility/loss evidence, deterministic fixtures, and review of the relevant standards sources.
