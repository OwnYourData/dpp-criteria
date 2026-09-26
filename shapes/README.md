# SHACL shapes

Passport checks with `check.type: shacl` validate the passport as RDF.

## Input preparation

A passport is served as plain JSON (EN 18223:2026 5.2). Before validation the
runner turns it into JSON-LD:

1. add the context from `en18223-context.jsonld`, which maps every JSON key to
   the namespace of the SOyA structure `DigitalProductPassport`
   (`https://soya.ownyourdata.eu/DigitalProductPassport/`, the same pattern as didlint uses for `Did`) and
   reads `objectType` as the RDF type of a data element;
2. add `"@type": "DigitalProductPassport"` to the top-level object.

Keys keep their spelling, so a key that differs from a published attribute name
(for example `DPPStatus`) stays visible to the shapes.

## Files

| File | Criterion | Content |
|---|---|---|
| `en18223-context.jsonld` | – | JSON-LD context for the input preparation |
| `en18223-dpp-core.ttl` | DPP-DAT-014 | Header attributes of EN 18223:2026 Table 1: names, cardinality, types, UTC timestamp |
| `en18223-dpp-model.ttl` | DPP-INT-005 | Data elements in the expanded full serialization (Annex A): objectType, Tables 2 to 6, unique elementId per level, values against valueDataType (Table 7) |

## Tests

Every shapes file has test vectors under `tests/shapes/<name>/`: `valid/` must
pass without results, `warning/` must pass with at least one warning,
`invalid/` must fail with at least one violation. Each invalid vector contains
exactly one fault. Run them with:

```
pip install pyshacl==0.30.1
python scripts/test_shapes.py
```
