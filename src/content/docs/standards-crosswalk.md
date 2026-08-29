---
title: Standards crosswalk

description: See how MeaningWire relates to public interoperability standards and comparative data-model approaches without claiming equivalence, certification, affiliation, or endorsement.
---

MeaningWire does not replace the standards on this page. It is designed to keep canonical meaning, explicit mappings, provenance, authority, and transformation evidence inspectable while systems continue to use the protocols, documents, vocabularies, and models appropriate to their own boundaries.

This page is an **informative crosswalk**, not a conformance statement. A reference here does not mean MeaningWire is certified by, affiliated with, endorsed by, or fully compatible with the referenced organization or specification.

## Classification used here

### NORMATIVE FOR MEANINGWIRE

A contract or external specification that the current public MeaningWire implementation actually depends on for defined behavior. MeaningWire's own versioned schemas, mapping registry, execution rules, provenance model, authority model, and validation rules remain the normative source for MeaningWire behavior.

### INFORMATIVE REFERENCE

A public standard or vocabulary that helps define an interoperability boundary or supplies useful domain semantics. MeaningWire may map to or from such a standard, but the standard does not become MeaningWire's canonical model merely because it is referenced.

### COMPARATIVE MODEL

A model or architecture whose ideas are useful for comparison. Comparative entries are not dependencies and do not imply compatibility, adoption, endorsement, or a plan to reproduce the model.

## NORMATIVE FOR MEANINGWIRE

### JSON Schema Draft 2020-12

**Scope:** JSON Schema defines a JSON-based language for describing JSON structure and validation behavior. The official project identifies Draft 2020-12 as its current published specification.

**MeaningWire relationship:** MeaningWire's current canonical schemas declare the Draft 2020-12 meta-schema, and CI validates those public contracts using that dialect. JSON Schema therefore supplies the external validation language for the current schema layer. MeaningWire still owns the semantics of its identifiers, canonical fields, mapping rules, provenance, authority, and maturity states.

**Boundary:** JSON Schema can describe and validate data shape and constraints; it does not by itself establish that two systems mean the same thing, authorize a mapping, transfer approval, or record transformation provenance.

Source: [JSON Schema specification](https://json-schema.org/specification)

## INFORMATIVE REFERENCE

### OpenAPI Specification

**Scope:** OpenAPI defines a language-agnostic description format for HTTP APIs. The current published specification is OpenAPI 3.2.0.

**MeaningWire relationship:** An adapter or future service boundary can use OpenAPI to describe HTTP operations while MeaningWire describes canonical semantics and explicit mappings behind that interface.

**Boundary:** OpenAPI describes an HTTP API contract. MeaningWire does not treat an OpenAPI schema or operation description as proof of semantic equivalence, mapping correctness, provenance, or human approval.

Source: [OpenAPI Specification 3.2.0](https://spec.openapis.org/oas/v3.2.0.html)

### AsyncAPI Specification

**Scope:** AsyncAPI describes message-driven APIs in a machine-readable, protocol-agnostic form. AsyncAPI 3.1.0 is the current published specification documented by the initiative.

**MeaningWire relationship:** AsyncAPI can describe channels, messages, operations, and protocol bindings at an asynchronous integration edge. MeaningWire can separately identify the canonical contracts and mappings applied to message payloads.

**Boundary:** AsyncAPI is an interface description contract for event-driven systems; it does not automatically make different payload models semantically equivalent or transfer source authority into a MeaningWire target.

Source: [AsyncAPI Specification 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0)

### CloudEvents

**Scope:** CloudEvents defines a common way to describe event data so event producers and consumers can share consistent event context across services, platforms, and systems.

**MeaningWire relationship:** CloudEvents is a useful transport/event-envelope boundary. A CloudEvent can carry data whose meaning is expressed through MeaningWire contracts and mappings, while CloudEvents continues to describe event context and delivery-facing metadata.

**Boundary:** MeaningWire does not replace CloudEvents, and a CloudEvents envelope does not define the complete business semantics of its payload.

Source: [CloudEvents](https://cloudevents.io/)

### OASIS Universal Business Language (UBL)

**Scope:** UBL 2.4 is an OASIS Standard defining reusable business information components and common business documents such as orders, invoices, and transport-related documents.

**MeaningWire relationship:** UBL can remain the authoritative document vocabulary at a business-document edge. MeaningWire can represent an explicit mapping between a UBL concept/document path and a canonical MeaningWire contract when a real integration requires one.

**Boundary:** MeaningWire does not import UBL wholesale as its canonical schema and does not claim UBL conformance unless a future adapter or mapping is separately implemented and tested against the applicable UBL requirements.

Source: [OASIS UBL 2.4](https://docs.oasis-open.org/ubl/UBL-2.4.html)

### Schema.org

**Scope:** Schema.org maintains a shared vocabulary for structured data on the Internet, including entities, relationships, and actions, with encodings including JSON-LD.

**MeaningWire relationship:** Schema.org terms can be useful identifiers or mapping targets for public/web-facing concepts where their published meaning fits the integration need.

**Boundary:** MeaningWire does not assume that similarly named Schema.org and MeaningWire concepts are equivalent. Any relationship must be explicit and reviewed like other mappings.

Source: [Schema.org](https://schema.org/)

### GS1 EPCIS and Core Business Vocabulary (CBV)

**Scope:** GS1 EPCIS defines interoperable visibility-event data and interfaces, while CBV supplies vocabulary structure and values used with EPCIS. GS1's current repository lists EPCIS 2.0.1 and CBV 2.0.0 artefacts.

**MeaningWire relationship:** EPCIS/CBV can remain authoritative for supply-chain visibility events at an integration boundary. MeaningWire may map selected event concepts into canonical contracts while preserving source identity and provenance.

**Boundary:** MeaningWire does not redefine EPCIS event conformance or CBV vocabulary rules. A future mapping must preserve the distinction between GS1-defined semantics and MeaningWire-defined canonical semantics.

Source: [GS1 EPCIS / CBV 2.0.1 artefacts](https://ref.gs1.org/standards/epcis/artefacts)

### OAGIS / connectSpec

**Scope:** The Open Applications Group renamed OAGIS (Open Applications Group Integration Specification) to connectSpec. OAGi describes its mission around interoperability through business-process models, data standards, ontologies, documentation, tools, and practices; the current connectSpec documentation exposes Business Object Document structures.

**MeaningWire relationship:** connectSpec business objects can be treated as an external business-language boundary. Explicit MeaningWire mappings can relate selected source/target concepts without absorbing the entire model.

**Boundary:** MeaningWire is not an OAGi implementation or conformance profile, and no mapping is implied merely because both projects address business interoperability.

Sources: [OAGIS and connectSpec naming/history](https://oagi.org/pages/oagis-and-score), [connectSpec Business Object Document](https://www.oagidocs.org/docs/business-object-document/)

### Financial Industry Business Ontology (FIBO)

**Scope:** FIBO is a formal financial-industry ontology, published in RDF/OWL, for defining financial concepts and relationships precisely and in machine-readable form.

**MeaningWire relationship:** FIBO can provide domain-semantic reference points for future finance mappings where the ontology's terms are appropriate.

**Boundary:** MeaningWire's current canonical contracts are not FIBO ontologies. Referencing a FIBO concept would require an explicit mapping and would not make MeaningWire FIBO-conformant or endorsed by EDM Council or OMG.

Source: [EDM Council — Financial Industry Business Ontology](https://edmcouncil.org/financial-industry-business-ontology/)

### JSON-LD 1.1

**Scope:** JSON-LD 1.1 is a W3C Recommendation for serializing Linked Data in JSON and associating JSON data with linked-data identifiers and vocabularies.

**MeaningWire relationship:** JSON-LD can be useful when a MeaningWire edge needs linked-data identifiers or RDF-compatible serialization without abandoning JSON-based integration.

**Boundary:** MeaningWire does not currently require JSON-LD for its canonical contracts. JSON-LD supplies a linked-data serialization/context mechanism; MeaningWire separately governs canonical contract identity, mappings, provenance, and authority.

Source: [W3C JSON-LD 1.1](https://www.w3.org/TR/json-ld11/)

## COMPARATIVE MODEL

### Microsoft Common Data Model (CDM)

Microsoft describes CDM as a shared data language and metadata system with standardized, extensible entities, attributes, semantic metadata, and relationships for business and analytical applications.

**Useful comparison:** CDM demonstrates the value of shared entity definitions and semantic metadata. MeaningWire differs by emphasizing a vendor-neutral public canonical layer plus explicit edge mappings, transformation provenance, fail-closed ambiguity handling, and authority boundaries rather than adopting Microsoft's entity set as its own.

Source: [Microsoft Common Data Model](https://learn.microsoft.com/en-us/common-data-model/)

### TM Forum Information Framework (SID)

TM Forum describes SID as an information/data reference model and common vocabulary for communications-service-provider business concepts, independent of platform, language, or protocol.

**Useful comparison:** SID is an example of a mature industry-specific reference model. MeaningWire can learn from that separation of vocabulary/model from implementation while remaining cross-domain and avoiding claims that its concepts are SID-compatible without explicit mappings and evidence.

Source: [TM Forum Information Framework (SID)](https://www.tmforum.org/open-digital-architecture/information-framework-sid/)

### National Information Exchange Model (NIEM)

NIEM describes itself as a common vocabulary for reusable information exchange across diverse public and private organizations. Its release packages include reference schemas and other model artefacts.

**Useful comparison:** NIEM demonstrates governed reusable vocabulary and exchange-package practices across communities of interest. MeaningWire remains a separate model and does not claim NIEM conformance; a future relationship would be expressed through explicit mappings and tested exchange boundaries.

Source: [NIEM 5.1 release](https://release.niem.gov/niem/5.1/)

### SAP One Domain Model concepts

SAP Master Data Integration documents integration models based on the SAP One Domain Model for exchanging master-data types such as business partners, equipment, cost centers, and other domain objects.

**Useful comparison:** The approach illustrates domain-level integration models with independently versioned business objects. MeaningWire can compare versioning and edge-integration ideas without depending on SAP models or representing itself as SAP-compatible.

Source: [SAP Master Data Integration — Integration Models](https://help.sap.com/docs/master-data-integration/sap-master-data-integration-prod/integration-models)

### Salesforce integration-pattern concepts

Salesforce publishes integration patterns for recurring enterprise integration scenarios rather than a single universal canonical schema.

**Useful comparison:** The pattern approach is a reminder that semantic normalization is only one part of integration architecture. MeaningWire's canonical contracts and mappings can be used inside an appropriate interaction pattern without replacing transport, orchestration, synchronization, or reliability design.

Source: [Salesforce Integration Patterns](https://architect.salesforce.com/docs/architect/fundamentals/guide/integration-patterns)

## How to read a future MeaningWire mapping

A future standards mapping should identify at least:

1. the exact source specification/model and version where a stable version exists;
2. the exact MeaningWire source or target contract identity;
3. source and target paths or terms;
4. mapping identity and version;
5. transformation behavior and known loss;
6. provenance showing what was transformed and by which registered mapping;
7. authority boundaries, including who may approve a target representation;
8. validation evidence for the exact implemented mapping.

A standards citation is not a mapping. A matching label is not semantic equivalence. A successful transformation is not approval.

**Approval is not transferred.**
