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
    kind: harmonised-standard   # regulation | harmonised-standard | draft-standard | standard | guidance | derived
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
catalogue_ref: DPP-API-013      # catalogue row(s) this criterion covers: one ID or a list
notes: ""
```

### Field rules

| Field | Rule |
|---|---|
| `id` | `DPP-<AREA>-<NNN>`. Areas follow the catalogue (API, DEX, ID, DAT, …). New criteria take the next free number in their area. A deprecated ID is never reused. |
| `version` | Integer, starts at 1. Bump when the statement, level, basis or check changes meaning. Typos do not bump. |
| `status` | New pull requests enter as `proposed`. A maintainer sets `active` after review. Only `active` criteria count in published results. |
| `statement` | English, one sentence, RFC 2119 keyword in capitals. Paraphrase the source. Do not paste text from licensed standards. |
| `basis` | At least one entry. `kind: harmonised-standard` is a standard cited in the Official Journal, `draft-standard` a standard not yet published or cited, `standard` any other published standard (ISO, W3C, …). `kind: derived` means an engineering inference from the other entries; it can never be the only entry of a `MUST`. |
| `target` | `passport`: observable by fetching a published passport (DPP linter). `service`: property of a DPP service (validator). `operator`: obligation of the economic operator; allowed only with `method: self-declared`. |
| `method` | `automated`: runs from the public internet with a test product identifier and test passport ID only. `automated-auth`: also needs test credentials supplied by the service operator. `self-declared`: the operator states conformance and links evidence; results show these separately and never as "passed". |
| `requires_features` | Feature flags from the controlled list below. Empty means "applies to every service". |
| `applies_if` | Passport criteria only. A list of JSON assertions (see `http`) on the fetched passport. If one does not hold, the result is `skipped`. |
| `catalogue_ref` | Catalogue rows whose check this criterion carries. Several rows that lead to the same check share one criterion, so a check counts only once in "N of M". |
| `check.type` | One of `http`, `tls`, `shacl`, `resolve`, `did`, `proof`, `links`, `declaration`. Each type is implemented once in the runner; a pull request that needs a new type adds it to the runner in the same PR. A check accepts only the fields listed for its type below; any other key, including a misspelt one, is a schema error. |

### Placeholders in checks

| Placeholder | Value |
|---|---|
| `{base}` | `api_base` of the service entry |
| `{dppId}` | `test_data.dppId` |
| `{productId}` | `test_data.productId` |
| `{elementIdPath}` | `test_data.elementIdPath`, the JSONPath of a data element in the test passport |
| `{randomId}` | An ID that no service has issued: the runner's name, `-` and 32 random lowercase hexadecimal digits (128 bits), e.g. `dpp-validator-3f9c…`. It uses only unreserved characters (RFC 3986), so encoding never changes it. |
| `{now}` | Run time in UTC as `YYYY-MM-DDThh:mm:ssZ` (RFC 3339, whole seconds) |

`{randomId}` and `{now}` are fixed once per run and are the same in every
criterion of that run. Only these six names are placeholders; any other text in
braces stays as written (e.g. the body `{not json` of DPP-API-007).

If a criterion uses a placeholder that has no value for the service (e.g.
`{elementIdPath}` without `test_data.elementIdPath`), the criterion is
`skipped` with that reason before any request is sent.

Where placeholders are substituted, and how:

- **Request `path`** (`http`): the value is percent-encoded. Every octet of
  its UTF-8 form outside the unreserved characters of RFC 3986
  (`A-Z a-z 0-9 - . _ ~`) is written as `%XX` with capital hex digits, so the
  value stays one path segment or one query value (`:`, `/`, `$`, `[` and `?`
  included). Text around the placeholders is sent as written in the
  criterion, so a criterion can contain encoded characters of its own (e.g.
  `%24%5B` in DPP-API-021).
- **Request `headers` and `body`**: the value is inserted as it is. In a body
  that is not a string, placeholders are substituted in the strings of the
  JSON value (member names and values) before it is serialised, so the value
  ends up correctly escaped as a JSON string. A string body is sent with the
  value inserted literally.
- **JSON assertions** (`path`, `equals`, `in`): in
  `equals` and `in` the value is inserted as it is. In a JSONPath a
  placeholder may stand only inside a string literal (`'…'` or `"…"`); the
  value is inserted escaped as RFC 9535 requires for that literal (`\` as
  `\\`, the enclosing quote with a backslash, control characters as
  `\uXXXX`), so it is compared literally whatever characters it contains. A
  placeholder outside a string literal makes the JSONPath unusable and the
  criterion `skipped` (see "Results").
- **Not substituted**: regular expressions (`matches`, `base_matches`) and
  header assertions (`expect.headers`) are used as written.

### Check types

- **http** — ordered `steps`, each with `request` (`method`, `path` relative to
  `{base}`, optional `headers`, `body`, `auth: none | token`) and `expect`
  (`status` list, `content_type`, `json` assertions with RFC 9535 JSONPath:
  `equals`, `exists`, `in`, `matches` (see "Regular expressions"), each with
  optional `severity: warning`; `headers` assertions on response header fields,
  see below; `body_equals_step: n` compares the body with that of step n). A
  string `body` is sent as is, any other value as JSON. A step may list
  `skip_if_status` (result `skipped`) and `warn_if_status` (result `warning`);
  `severity: warning` on a step turns any failure of that step into a
  `warning` (`error` is the default and need not be written). `base_matches` is a regular expression (see "Regular expressions") that must
  be found in the API base.
- **tls** — `min_version`, `reject_versions` (`ssl3`, `1.0`, …),
  `recommend_versions` (warning if missing), `https_redirect`,
  `valid_certificate`, `http_versions` with `require` and `reject` lists.
  `http_versions` is tested on the HTTPS port of the API base only; plain HTTP
  on port 80 (redirect to HTTPS, ACME HTTP-01 challenges) is out of scope and
  covered by `https_redirect`. For each version in `reject` the runner sends
  `GET {base}/dpps/{dppId}` over TLS, forced to that version (ALPN offers only
  that protocol, no upgrade to another version). The version counts as
  **rejected** if no successful response comes back: the connection or the TLS
  handshake is aborted (including an ALPN `no_application_protocol` alert), the
  connection is closed or times out without a response, or the status is 400 or
  higher (505 HTTP Version Not Supported is the recommended answer). A 2xx or
  3xx status means the version is **not rejected**. As a reference, the same
  request is sent once with the runner's default negotiation; if that does not
  answer 2xx or 3xx, a 4xx or 5xx at the forced version says nothing about the
  version and the result is `skipped`.
- **shacl** — `structure`: name of a SOyA structure under `soya/`, published on
  soya.ownyourdata.eu. The passport fetched via `{productId}` is validated with
  `soya validate <structure>`; the results whose message starts with the
  criterion ID in brackets belong to the criterion (see
  [soya/README.md](soya/README.md)). Alternatively
  `shapes_select: content-specification | semantic-repository` picks shapes by
  the passport's `contentSpecificationIds` or from the Commission's semantic
  repository (none found → `skipped`).
- **resolve** — follow `{productId}` like a phone scanning a data carrier
  (plain HTTPS GET, no special headers). Without `expect` it expects a single
  passport object whose `uniqueProductIdentifier` equals the input; with
  `expect` those assertions apply instead. `accept` sets the Accept header.
  `further_requests` lists more requests to the same identifier, each with its
  own `accept` and `expect` and an optional `severity: warning` that turns any
  failure of that request into a `warning`; they run after the first request
  and are evaluated independently of it.
  `history.fail_after_consecutive_days` rates the criterion from the
  validator's daily runs only.
  Example (the first request must succeed; the header assertion and the second
  request only give warnings):

  ```yaml
  check:
    type: resolve
    accept: text/html
    expect:
      status: [200]
      content_type: text/html
      headers:
        - { name: Vary, contains: Accept, severity: warning }
    further_requests:
      - accept: "*/*"
        severity: warning
        expect:
          status: [200]
          content_type: application/json
  ```
- **did** — resolves the DIDs found at `paths` (non-DID values are skipped) and
  checks DID Core, DID Resolution and associated credentials against
  `vc_data_model`.
- **proof** — verifies the integrity proofs of the passport in `formats`
  (`vc-data-integrity`, `vc-jose-cose`, `did-oyd-log`), each with the key it
  names; no proof → `skipped`. With `key_from`, at least one verified proof has
  to be issued with a key of the DID at that path; otherwise a warning.
- **links** — checks every element of `element_type` for the `required`
  attributes and whether its URL answers; `unreachable` sets the severity.
- **declaration** — for `self-declared`: the service file must contain an entry
  under `declarations` with this criterion's ID, a `statement` and an
  `evidence` URL. The runner only checks presence and that the URL answers.

### Header assertions

`expect.headers` (in `http` and `resolve`) is a list of assertions on response
header fields. `name` is the field name, matched case-insensitively; several
fields with the same name are combined into one comma-separated value
(RFC 9110 5.3). Each assertion has at least one of: `exists` (true/false),
`equals` (whole value, exact), `contains` (the value, split at commas and
trimmed, has a member equal to this string, compared case-insensitively),
`matches` (regular expression searched in the combined value, see "Regular
expressions"). A missing field fails every assertion except `exists: false`.
`severity: warning` works as for JSON assertions.

### Order of evaluation within a request

For each request (an `http` step, the first `resolve` request or one of its
`further_requests`), `status` and `content_type` are evaluated first. Only if
both hold are `headers`, `json` and `body_equals_step` of the same `expect`
evaluated; otherwise they are not evaluated and give no message of their own,
because they would describe a different response than the one the criterion
is about. The failed `status` or `content_type` alone decides the outcome of
that request.

`content_type` compares the media type of the response without its parameters
(`charset` and the like), case-insensitively. If it names a JSON media type
(`application/json` or a `+json` type), the body must also parse as JSON, and
this belongs to the `content_type` check. In `resolve` the body must moreover
be a single JSON object, since the request fetches one passport; in `http` any
JSON value is accepted (a data element in the compressed representation may be
a bare value, see DPP-API-021).

### Regular expressions

`matches` in JSON and header assertions and `base_matches` use ECMA-262
(JavaScript) regular expression syntax, the same dialect as the JSON Schema
keyword `pattern`, without flags; CI rejects patterns that are not valid
ECMA-262. The pattern is searched anywhere in the value, not implicitly
anchored: write `^` and `$` to match the whole value. Matching is
case-sensitive. To stay portable across runners, use only literals, character
classes, quantifiers, alternation, groups and the anchors `^` and `$`; no
inline flags such as `(?i)`, lookaround, backreferences or named groups.
Patterns must not depend on how characters outside the Basic Multilingual
Plane are counted (ECMA-262 without flags counts UTF-16 code units, other
engines count code points); results in such cases are not defined. The same
rules apply to `matches` in `applies_if`, which uses JSON assertions.

Regular expressions inside a JSONPath expression, i.e. the arguments of the
RFC 9535 functions `match()` (whole value) and `search()` (anywhere in the
value), follow RFC 9535 and therefore I-Regexp (RFC 9485), not ECMA-262.
Such patterns must be valid I-Regexp and must not contain `^` or `$` outside a
character class: use `match()` for a whole-value match and `search()` for a
match anywhere. A runner checks these patterns before evaluating the JSONPath;
an invalid pattern, or one with `^` or `$`, is treated as unusable (see
"Results") instead of letting the function return false.

`matches` holds only if the value is a JSON string in which the pattern is
found. A number, boolean, `null`, array or object never satisfies `matches`
and is not converted to a string; use `equals` or `in` for those.

### Results

Each run gives every applicable criterion one result: `passed`, `failed`,
`warning` (passed, with a remark) or `skipped` (condition not met, feature not
declared or data not available). Only `passed` and `failed` enter "N of M".

A regular expression that the runner cannot evaluate as specified above
(invalid, or valid but outside the portable subset; for JSONPath functions an
invalid I-Regexp or one containing `^` or `$`) makes the criterion
`skipped` with that reason, before any request is sent. It never leads to
`failed`. CI already rejects patterns that are not valid ECMA-262. The same
holds for a JSONPath that is not valid RFC 9535 after substitution, or that
has a placeholder outside a string literal (see "Placeholders in checks").

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
  elementIdPath: $.ProductIdentification.ModelIdentifier   # needed for fine-granular-api
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
