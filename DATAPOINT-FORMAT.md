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
regime: ESPR                    # ESPR | TOY | CPR | EUDR | BATT
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
| `regime` | The legal act that defines the data point: `ESPR` (Regulation (EU) 2024/1781 and its delegated and implementing acts), `TOY` (Regulation (EU) 2025/2509), `CPR` (Regulation (EU) 2024/3110), `EUDR` (Regulation (EU) 2023/1115), `BATT` (Regulation (EU) 2023/1542). |
| `term` | The term of the English version of the legal act. |
| `en18223_attribute` | Only when an attribute of the class `DigitalProductPassport` (EN 18223:2026, Table 1) carries exactly this value. |
| `description` | English, paraphrased. |
| `battery_applicability` | Required for `BATT`, not allowed for other regimes. See "Battery data points" below. |
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
| `regime` | Required by a product-specific regulation (TOY, CPR, BATT). |
| `sectoral` | Required by sectoral law outside the DPP rules (EUDR). |

## Battery data points

The data points of the regime `BATT` cover the battery passport, which LMT
batteries, industrial batteries with a capacity greater than 2 kWh and electric
vehicle batteries need from 18 February 2027 (Regulation (EU) 2023/1542,
Art. 77(1)). They follow the European Commission's
[Guidance Document: Digital Batteries Passport – data points by category, version 2.0 of 15 August 2026](https://single-market-economy.ec.europa.eu/document/download/cd1e5e6c-4a4a-4b99-995a-49eb6916187e_en)
(© European Union, 2026, reused under CC BY 4.0): `DP-BATT-001` to `DP-BATT-071`
carry the numbers of the guidance, and each file names the guidance data point
in `basis` with `kind: guidance`, next to the clause of the Regulation. Names
and descriptions are paraphrased; access and granularity come from the
Regulation. The guidance is not legally binding.

Clauses refer to the Regulation as consolidated on 13 August 2026
(CELEX 02023R1542-20260813), which includes the corrigendum to Annex XIII,
point 1(q). A data point that the guidance lists but the Regulation does not
contain has only the guidance in `basis` and says so in `notes`
(`DP-BATT-044`).

- `access`: Annex XIII point 1 and Art. 77(3) are `public`; Annex XIII points 2,
  3 and 4 are `restricted` (Art. 77(2)), and `access_notes` names who may access
  them.
- `granularity`: `battery model` for Annex XIII points 1 to 3, `individual battery`
  for point 4 and for the identifier and the responsible operator (Art. 77(3)).

`battery_applicability` states for each battery category whether the data point
is to be provided:

```yaml
battery_applicability:
  ev:                           # electric vehicle batteries
    status: mandatory
  lmt:                          # LMT batteries
    status: not-to-be-filled
    reason: applies-later
    applies_from: "2027-08"
  industrial:                   # industrial batteries > 2 kWh
    status: if-applicable
    note: Only for some industrial batteries.
```

| Field | Rule |
|---|---|
| `ev`, `lmt`, `industrial` | All three are required. |
| `status` | `mandatory`, `optional` (to be provided if the information is available), `if-applicable` (where the condition in `note` applies) or `not-to-be-filled` (not to be provided or displayed). |
| `reason` | Required with `not-to-be-filled`, not allowed otherwise: `repetition` (the same information is provided under `same_as`), `pending-implementing-act`, `pending-delegated-act` (the act that specifies the information has not been adopted), `applies-later` (required from `applies_from`), `on-hold` (set aside by the guidance), `not-for-category` (does not apply to this battery category). |
| `same_as` | Required with `repetition`, only allowed there: the `DP-BATT` IDs that already carry the information. |
| `applies_from` | Required with `applies-later`: `YYYY-MM-DD`, or `YYYY-MM` where only the month is named. Without it, a data point applies from 18 February 2027. |
| `note` | Optional, English, paraphrased. |

When the guidance or the Regulation changes the applicability, the data point
gets the new values and its `version` is bumped.

## Identifiers

Data point IDs are independent of criterion IDs. A data point keeps its ID when
its wording changes; if its meaning changes, its `version` is bumped.

After changing a data point, run `python3 scripts/render_datapoints_md.py`
(needs `pip install pyyaml`) and commit the updated `datapoints/README.md`; CI
checks that it matches the YAML files.
