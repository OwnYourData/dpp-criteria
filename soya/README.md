# SOyA structures

Passport checks with `check.type: shacl` validate a passport with
[SOyA](https://github.com/OwnYourData/soya): `soya validate <structure>`. Each
structure in this folder is published on soya.ownyourdata.eu under its name.

| Structure | Criteria | Content |
|---|---|---|
| `DigitalProductPassport` | DPP-DAT-014, DPP-INT-005 | Classes of EN 18223:2026 4.1.2; header attributes of Table 1; data elements in the expanded full serialization (Annex A) with Tables 2 to 7 |

## Conventions

- **Messages carry the criterion.** Every validation message starts with the
  criterion ID in brackets, for example `[DPP-DAT-014]`. A tool that runs
  `soya validate` assigns results to criteria by this prefix.
- **Simple rules use `OverlayValidation`** (cardinality, pattern, message).
- **Other SHACL Core rules use overlays of type `OverlayShacl`.** They are
  written as JSON-LD node shapes; `soya init` takes overlays of an unknown type
  over unchanged, so `soya validate` applies them. Terms without prefix resolve
  to the structure's namespace.
- **Severity sits on the shape that reports.** For a rule inside `sh:property`,
  `sh:severity` belongs on that property shape.
- **`sh:targetClass` only for classes every passport has.** `soya validate`
  reports "Missing class" for every target class absent from the data. Rules for
  data elements therefore target `sh:targetObjectsOf` `elements` (and `value`)
  and apply to a type through `sh:or` with `sh:not`/`sh:class`.

## Limits

SOyA validates with SHACL Core (rdf-validate-shacl), without SHACL-SPARQL.
Rules that compare sibling nodes are therefore not checked, in particular that
an `elementId` is unique at its level (EN 18223 Table 2). Attribute names that
differ from the published ones only in spelling fail because the published
attribute is missing.

## Input preparation

As in didlint, the passport JSON is wrapped before validation:

```json
{
  "@context": {
    "@version": 1.1,
    "@vocab": "https://soya.ownyourdata.eu/DigitalProductPassport/",
    "objectType": "@type"
  },
  "@graph": [ { "@type": "DigitalProductPassport", "...": "passport attributes" } ]
}
```

## Tests

Test vectors live in `tests/soya/<structure>/<criterion>/`: `valid/` gives no
result for the criterion, `warning/` at least one warning and no violation,
`invalid/` at least one violation. Each invalid vector contains exactly one
fault. The runner uses soya-js, the library behind `soya validate`
(Node.js 20):

```
npm install --no-save soya-js@0.8.12
node scripts/test_structures.js
```
