# SOyA structures

Passport checks with `check.type: shacl` validate a passport with
[SOyA](https://github.com/OwnYourData/soya). Each structure in this folder is
published on soya.ownyourdata.eu under its name.

```
curl -s -H 'Accept: application/json' <product identifier> \
  | soya acquire DigitalProductPassport \
  | soya validate DigitalProductPassport
```

`soya acquire` turns the passport JSON into JSON-LD in the structure's
namespace; no further preparation is needed.

| Structure | Criteria |
|---|---|
| `DigitalProductPassport` | DPP-DAT-014 (header, EN 18223 Table 1), DPP-INT-005 (data elements, expanded full serialization of Annex A, Tables 2 to 7), DPP-ROL-016, DPP-DAT-015, DPP-ID-014, DPP-CAR-002, DPP-ID-009, DPP-ID-010, DPP-CFG-005 |

## Conventions

- **Messages carry the criterion.** Every validation message starts with the
  criterion ID in brackets, for example `[DPP-DAT-014]`. A tool that runs
  `soya validate` assigns results to criteria by this prefix.
- **Simple rules use `OverlayValidation`** (cardinality, pattern, message).
- **Other SHACL Core rules use overlays of type `OverlayShacl`.** They are
  written as JSON-LD node shapes; `soya init` takes overlays of an unknown type
  over unchanged, so `soya validate` applies them. Terms without prefix resolve
  to the structure's namespace.
- **Lists.** `soya acquire` turns attributes declared as `set<…>` (such as
  `elements`) into RDF lists. Shapes reach their items with the path
  `( elements [ sh:zeroOrMorePath rdf:rest ] rdf:first )`; rules for data
  elements target `sh:targetObjectsOf rdf:first` and `value`.
- **Types.** `objectType` stays a plain attribute; rules for one kind of data
  element apply through `sh:or` with `sh:not` and `sh:hasValue` on `objectType`.
- **`value` is not typed in the bases.** Its type depends on the kind of data
  element (any JSON value, a list of data elements, a list of language values);
  a single declared type would make `soya acquire` coerce the others.
- **`sh:targetClass` only for `DigitalProductPassport`.** `soya validate`
  reports "Missing class" for every target class without an instance in the
  data.
- **Severity sits on the shape that reports.** For a rule inside `sh:property`,
  `sh:severity` belongs on that property shape.

## Limits

SOyA validates with SHACL Core (rdf-validate-shacl), without SHACL-SPARQL.
Rules that compare sibling nodes are therefore not checked, in particular that
an `elementId` is unique at its level (EN 18223 Table 2). Attribute names that
differ from the published ones only in spelling fail because the published
attribute is missing. Identifier schemes (EN 18219 Clauses 5 and 6) are checked
by syntax only.

## Tests

Test vectors live in `tests/soya/<structure>/<criterion>/`: `valid/` gives no
result for the criterion, `warning/` at least one warning and no violation,
`invalid/` at least one violation. Each invalid vector contains exactly one
fault.

The tests run in the image `oydeu/soya-web-cli`, the same SOyA version that
dpplint uses, and need only Docker:

```
sh scripts/run_structure_tests.sh
```

The script builds every structure with `soya init` into `build/structures/`,
embeds the imported SOyA context, serves the result as a local repository
inside the container and sends each vector through the web-cli endpoints
`acquire` and `validate`. Nothing is loaded from soya.ownyourdata.eu.
