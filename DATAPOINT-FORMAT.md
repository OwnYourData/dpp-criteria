# Data point format

Every data point is one YAML file under `datapoints/<regime>/<ID>.yaml`. A data
point is something an EU legal act requires, allows or expects in a digital
product passport. Data points are reference material: criteria can be derived
from them, but they are not checked themselves. The format is checked in CI
against `schema/datapoint.schema.json`; `datapoints/README.md` lists all data
points in readable form.

## Data point

```yaml
id: DP-ESPR-002                 # stable, never reused; see "Identifiers" below
version: 1                      # bump on any change of meaning
regime: ESPR                    # ESPR | TOY | CPR | EUDR
tier: fixed                     # see "Tiers" below
name: Manufacturer contact details
term: manufacturer name, registered trade name or registered trade mark, postal address, electronic means of communication
description: >-                 # paraphrase, never a quotation of licensed standard text
  Name, registered trade name or registered trade mark, postal address with a single
  contact point and electronic means of communication of the manufacturer, in the
  public part of the digital product passport.
granularity: model, or as set by the delegated act
provided_by: manufacturer
access: public                  # public | restricted | delegated-act | unspecified
access_notes: >-
  Art. 27(6), first subparagraph, point (a) places the details on the public part of
  the passport, where applicable.
basis:
- source: Regulation (EU) 2024/1781 (ESPR)
  clause: Art. 27(6), first subparagraph, point (a); Annex III, point (g)
  kind: regulation
  url: https://eur-lex.europa.eu/eli/reg/2024/1781/oj
notes: ""
```

### Field rules

| Field | Rule |
|---|---|
| `id` | `DP-<REGIME>-<NNN>`. New data points take the next free number of their regime. A removed ID is never reused. |
| `version` | Integer, starts at 1. Bump when the description, access or basis changes meaning. Typos do not bump. |
| `regime` | The legal act that defines the data point: `ESPR` (Regulation (EU) 2024/1781 and its delegated and implementing acts), `TOY` (Regulation (EU) 2025/2509), `CPR` (Regulation (EU) 2024/3110), `EUDR` (Regulation (EU) 2023/1115). |
| `term` | The term of the English version of the legal act. |
| `en18223_attribute` | Only when an attribute of the class `DigitalProductPassport` (EN 18223:2026, Table 1) carries exactly this value. |
| `description` | English, paraphrased. |
| `access` | `public`: the act puts the value in the public part, or requires it on the product or via the data carrier without access restriction. `restricted`: the act limits it to named actors. `delegated-act`: the act leaves the access class to a delegated or implementing act. `unspecified`: the act says nothing about access. |
| `basis` | At least one entry, same fields and `kind` values as in criteria (see [CRITERIA-FORMAT.md](CRITERIA-FORMAT.md)). Clauses in the notation of the English Official Journal, e.g. `Art. 27(6), first subparagraph, point (a)`, `Annex III, point (g)`. |

### Tiers

| Tier | Meaning |
|---|---|
| `fixed` | ESPR fixes the data point for every passport. |
| `minimum` | ESPR fixes it as minimum content; the delegated act may narrow it. |
| `conditional` | Required when a condition set directly in ESPR or the registry regulation applies. |
| `delegated-act` | The delegated act selects it from ESPR Annex III. |
| `annex-i` | Product parameter from ESPR Annex I, selectable by the delegated act. |
| `voluntary` | Voluntary information within the frame of the delegated act. |
| `regime` | Required by a product-specific regulation (TOY, CPR). |
| `sectoral` | Required by sectoral law outside the DPP rules (EUDR). |

## Identifiers

Data point IDs are independent of criterion IDs. A data point keeps its ID when
its wording changes; if its meaning changes, its `version` is bumped.

After changing a data point, run `python3 scripts/render_datapoints_md.py`
(needs `pip install pyyaml`) and commit the updated `datapoints/README.md`; CI
checks that it matches the YAML files.
