# Criteria format

Every criterion is one YAML file under `criteria/<area>/<ID>.yaml`. Every listed
DPP service is one YAML file under `services/<slug>.yaml`. One file per entry
keeps pull requests small and free of merge conflicts. Both formats are checked
in CI against the JSON Schemas in `schema/`.

## Criterion

```yaml
id: DPP-API-013                 # stable, never reused; see "Identifiers" below
version: 1                      # bump on any change of meaning
status: active                  # proposed | active | deprecated
title: Lifecycle API provides ReadDPPById
statement: >-                   # paraphrase, never a quotation of licensed standard text
  The DPP lifecycle API MUST provide the method ReadDPPById.
level: MUST                     # MUST | SHOULD | MAY
basis:
  - source: EN 18222:2026
    clause: "4.2"
    kind: harmonised-standard   # regulation | harmonised-standard | draft-standard | guidance | derived
target: service                 # passport | service | operator
method: automated               # automated | automated-auth | self-declared
requires_features: []           # criterion applies only if the service declares all of these
check:                          # required for automated / automated-auth
  type: http
  steps:
    - request: { method: GET, path: "/dpps/{dppId}" }
      expect:
        status: [200]
        content_type: application/json
        json:
          - { path: "$.digitalProductPassportId", equals: "{dppId}" }
catalogue_ref: DPP-API-013      # row in the source catalogue, if any
notes: ""
```

### Field rules

| Field | Rule |
|---|---|
| `id` | `DPP-<AREA>-<NNN>`. Areas follow the catalogue (API, DEX, ID, DAT, …). New criteria take the next free number in their area. A deprecated ID is never reused. |
| `version` | Integer, starts at 1. Bump when the statement, level, basis or check changes meaning. Typos do not bump. |
| `status` | New pull requests enter as `proposed`. A maintainer sets `active` after review. Only `active` criteria count in published results. |
| `statement` | English, one sentence, RFC 2119 keyword in capitals. Paraphrase the source. Do not paste text from licensed standards. |
| `basis` | At least one entry. `kind: derived` means an engineering inference from the other entries; it can never be the only entry of a `MUST`. |
| `target` | `passport`: observable by fetching a published passport (DPP linter). `service`: property of a DPP service (validator). `operator`: obligation of the economic operator; allowed only with `method: self-declared`. |
| `method` | `automated`: runs from the public internet with a test product identifier and test passport ID only. `automated-auth`: also needs test credentials supplied by the service operator. `self-declared`: the operator states conformance and links evidence; results show these separately and never as "passed". |
| `requires_features` | Feature flags from the controlled list below. Empty means "applies to every service". |
| `check.type` | One of `http`, `tls`, `shacl`, `resolve`, `declaration`. Each type is implemented once in the runner; a pull request that needs a new type adds it to the runner in the same PR. |

### Placeholders in checks

`{base}` API base URL of the service · `{dppId}` test passport ID · `{productId}`
test product identifier (URL-encoded where used in a path) · `{now}` run time
(ISO 8601, UTC).

### Check types

- **http** — ordered `steps`, each with `request` (`method`, `path`, optional
  `headers`, `body`, `auth: none | token`) and `expect` (`status` list,
  `content_type`, `json` assertions with RFC 9535 JSONPath: `equals`, `exists`,
  `in`, `matches`).
- **tls** — `min_version`, `reject_versions`, `https_redirect: true|false`.
- **shacl** — `shapes`: path to a Turtle file under `shapes/`; input is the
  passport fetched via `{productId}`.
- **resolve** — follow `{productId}` like a phone scanning a data carrier
  (plain HTTPS GET, no special headers), expect a passport whose
  `uniqueProductIdentifier` equals the input.
- **declaration** — for `self-declared`: the service file must contain an entry
  under `declarations` with this criterion's ID, a `statement` and an
  `evidence` URL. The runner only checks presence and that the URL answers.

### Controlled feature flags

`fine-granular-api`, `write-api`, `historical-versions`, `access-levels`,
`backup-provider`, `registry-integration`, `battery`, `pcds`.

## Service

```yaml
id: ownyourdata-dpp-service
name: OwnYourData DPP Service
operator:
  name: OwnYourData
  url: https://www.ownyourdata.eu
contact: TODO                          # address for questions about results
api_base: https://dpp-service.ownyourdata.eu/dpp/v1
features: [fine-granular-api, write-api, historical-versions]
test_data:
  productId: https://dpp.oydapp.eu/01/09520123456788/21/000001
  dppId: did:oyd:zQmTMPiMZ6mUg5bVXQxkuZ1JCgmtKE9QNu514EdMUydq9zL
credentials: none                     # none | secret:<NAME>  (repository secret, never in the file)
declarations:
  - criterion: DPP-OPS-006
    statement: Test and production environments are separated.
    evidence: https://example.org/ops-doc
listed_since: 2026-10-01
```

Rules:

- Services are listed **only by pull request from the operator** (or with the
  operator's written consent linked in the PR). No third party is tested
  without that.
- `test_data` must point to a passport that stays online for as long as the
  service is listed. It is ideally a passport made for this purpose.
- Credentials are never stored in the repository. An operator who wants
  `automated-auth` checks provides a test token as a repository secret via the
  maintainers.

## Results wording

Results report "N of M automated checks passed" per service and run, plus the
list of self-declarations. They never state that a service is "conformant"
or "certified": passing checks is not a presumption of conformity.

## Identifiers

IDs from the catalogue (`DPP System Requirements Katalog v2`) keep their
number. Criteria that do not come from the catalogue take the next free number
in their area.
