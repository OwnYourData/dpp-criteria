# Adding or correcting a DPP service

This guide explains how the operator of a Digital Product Passport (DPP)
service adds the service to the list checked every day by
[dpp-validator](https://github.com/OwnYourData/dpp-validator), and how an
operator corrects or takes over an entry from our own research. The results
are published at <https://ownyourdata.github.io/dpp-validator/>, together with
`available-services.json`, the list of all entries with their latest results.

The list has two kinds of entries (`entry.source`):

- **Entries maintained by the operator** (`operator`): added by the operator's
  pull request, or with the operator's consent linked in the pull request.
  Checked in full every day.
- **Entries from our research** (`research`): services we found in our own
  research, from public information. They are marked as such wherever results
  are shown and may be incomplete or out of date. They are checked read-only
  at most once a week, or not at all if that is not possible (see
  [section 7](#7-entries-from-our-research)).

This list is part of a research project. It shares what we currently know; it
makes no claim to be complete and is not a legal assessment. Results are
results of automated checks only. They are no certification and establish no
presumption of conformity.

## Contents

1. [What is checked](#1-what-is-checked)
2. [Before you start](#2-before-you-start)
3. [The service entry](#3-the-service-entry)
4. [Check your entry locally](#4-check-your-entry-locally)
5. [Open the pull request](#5-open-the-pull-request)
6. [After the merge](#6-after-the-merge)
7. [Entries from our research](#7-entries-from-our-research)
8. [Questions](#8-questions)

## 1. What is checked

Every day at about 04:17 UTC, dpp-validator runs all service criteria of this
repository (`target: service`, `method: automated`) against every operator
entry in this directory, and checks the passports in `example_passports` with
dpplint. Research entries are checked the same way once a week, read-only.
Examples:

| Area | Examples of criteria |
|---|---|
| Transport (EN 18216 Clause 4) | HTTPS with a valid certificate, TLS 1.2 or higher, HTTP/2, no HTTP versions below HTTP/2 |
| Lifecycle API (EN 18222) | ReadDPPById, ReadDPPByProductId, ReadDPPIdsByProductIds, version prefix `v1/`, status codes, 404 for unknown passports, the `representation` query flag |
| Protection | a passport cannot be created or changed without authorisation |

The readable list of all criteria is [criteria/README.md](../criteria/README.md).

Only criteria with `status: active` count in "N of M automated checks
passed". A criterion that does not apply is reported as `skipped` with a
reason code (`not_applicable`, `not_implemented`, …) and never counts against
the service.

The content of the test passport (data model, identifiers, integrity proofs)
can be checked at any time with [dpplint](https://dpplint.ownyourdata.eu).

## 2. Before you start

You need:

- **A public DPP API following EN 18222**, reachable over HTTPS, with the
  version prefix `v1/` in its paths, for example
  `https://dpp.example.org/api/v1`.
- **A test passport** that stays online for as long as the service is listed.
  Ideally a passport made for this purpose, with public data only.
- **An e-mail address** for questions about the results. It is shown on the
  results page.
- **A GitHub account**, `git` and Docker on your computer (for the local check
  in step 4).

What the daily run sends to your service:

- About 30 requests and TLS handshakes per day, one after the other. No load
  tests.
- Read requests: GET to the test passport and to an ID that does not exist,
  and `POST {api_base}/dppsByProductIds` with a list containing the
  `productId` of the test passport (ReadDPPIdsByProductIds).
- One plain HTTP request on port 80, to check that it is redirected to HTTPS
  or refused.
- **Requests without credentials that must be refused.** The run checks that
  nobody can create or change a passport without authorisation:

  | Request | Body | Expected answer |
  |---|---|---|
  | `PATCH {api_base}/dpps/{dppId}` | `{}` | 400, 401, 403, 404, 405 or 501 |
  | `POST {api_base}/dpps` | `{}` | 400, 401, 403, 404, 405 or 501 |
  | `POST {api_base}/dppsByProductIds` | `{not json` and `{"productId": 42}` | 400 |

  The PATCH body changes nothing, and no DELETE is ever sent. Afterwards the
  run reads the test passport again and checks that it is unchanged.

Please make sure your service accepts these requests from the internet and
answers them without changing data.

## 3. The service entry

A service is listed by one YAML file in this directory, named after its
`id`: `services/<id>.yaml`. The format is defined in
[CRITERIA-FORMAT.md](../CRITERIA-FORMAT.md#service) and checked against
[schema/service.schema.json](../schema/service.schema.json).

### Example

```yaml
id: example-dpp-service
name: Example DPP Service
url: https://dpp.example.org/
operator:
  name: Example GmbH
  url: https://www.example.org
  country: DE
entry:
  source: operator
  as_of: 2026-10-15
licence:
  text: Apache-2.0
  spdx: [Apache-2.0]
source_code: https://github.com/example/dpp-service
example_passports:
  - product_id: https://dpp.example.org/01/09520123456788/21/000001
    label: test passport
check:
  mode: full-daily
contact: dpp@example.org
api_base: https://dpp.example.org/api/v1
features: [fine-granular-api]
not_implemented: [write-api, historical-versions]
test_data:
  productId: https://dpp.example.org/01/09520123456788/21/000001
  dppId: https://dpp.example.org/dpp/000001
  elementIdPath: $.ProductIdentification.ModelIdentifier
credentials: none
declarations: []
listed_since: 2026-10-15
```

A real entry: [ownyourdata-dpp-service.yaml](ownyourdata-dpp-service.yaml).

### Fields

| Field | Required | What to enter | Example |
|---|---|---|---|
| `id` | yes | Short name of the service: lower-case letters, digits and hyphens. The file name must be `<id>.yaml`. | `example-dpp-service` |
| `name` | yes | Name shown on the results page. | `Example DPP Service` |
| `url` | no | Web page of the service. | `https://dpp.example.org/` |
| `operator.name` | yes | Legal name of the operator. | `Example GmbH` |
| `operator.url` | no | Website of the operator. | `https://www.example.org` |
| `operator.country` | no | Country of the operator's seat, ISO 3166-1 alpha-2 in capitals. | `DE` |
| `entry.source` | yes | `operator` for an entry by the operator or with its consent. | `operator` |
| `entry.as_of` | yes | Date on which the information in the entry was last checked. | `2026-10-15` |
| `licence.text` | yes | Licence as shown to people; for a commercial service with open parts, say so. | `Apache-2.0` |
| `licence.spdx` | yes | SPDX identifiers of the licences of the software; `[]` if none applies. | `[Apache-2.0]` |
| `source_code` | no | Public repository of the software. | `https://github.com/example/dpp-service` |
| `example_passports` | no | Up to three published passports, each with `product_id` (an `https://` product identifier) and `label`. They are checked with [dpplint](https://dpplint.ownyourdata.eu) in each run. | see the example |
| `check.mode` | yes | `full-daily` for an operator entry. | `full-daily` |
| `contact` | yes | E-mail address for questions about the results; shown as a mailto link. | `dpp@example.org` |
| `api_base` | yes | Base URL of the EN 18222 API, `https://`, ending with the version prefix `v1`. The criteria append paths such as `/dpps/{dppId}`. | `https://dpp.example.org/api/v1` |
| `features` | yes | Optional parts of the standard the service offers (list below). An empty list `[]` is allowed. | `[fine-granular-api]` |
| `not_implemented` | no | Optional parts that concern the service but are not available yet. Their criteria are reported as `not_implemented` instead of `not_applicable`. A flag may not be in `features` and `not_implemented` at the same time. | `[write-api, historical-versions]` |
| `test_data.productId` | yes | Exactly the value of `uniqueProductIdentifier` in the test passport. Ideally an HTTPS URL that resolves to the passport (EN 18219). Used in `ReadDPPByProductId`. | `https://dpp.example.org/01/09520123456788/21/000001` |
| `test_data.dppId` | yes | Exactly the value of `digitalProductPassportId` in the test passport. Used in `ReadDPPById`; the run percent-encodes it in the path. | `https://dpp.example.org/dpp/000001` or `did:example:123` |
| `test_data.elementIdPath` | with `fine-granular-api` | RFC 9535 JSONPath of one data element of the test passport, in the compressed representation (EN 18223 5.2: element IDs as keys). | `$.ProductIdentification.ModelIdentifier` |
| `test_data.controlledElementId` | with `access-levels` | `elementId` of one controlled data element of the test passport: an element that a request without credentials must not receive. For battery passports an element of Annex XIII point 3 of the Batteries Regulation (results of test reports). | `DismantlingInformation` |
| `test_data.controlledElementIdPath` | with `access-levels` and `fine-granular-api` | RFC 9535 JSONPath of that controlled element in the compressed representation. | `$.DismantlingInformation` |
| `credentials` | yes | Always `none` for now: checks that need test credentials are not run yet. Never put secrets into this repository. | `none` |
| `declarations` | no | Self-declarations for criteria with `method: self-declared`, each with `criterion`, `statement` and an `evidence` URL. They are listed, never counted as passed. | see below |
| `consent` | if the PR is not opened by the operator | Link to the operator's written consent. | `https://github.com/OwnYourData/dpp-criteria/issues/42` |
| `notes` | no | Remarks shown with the entry. | `Test passport made for the checks.` |
| `listed_since` | yes | Date of the pull request (`YYYY-MM-DD`); the maintainers set the date of the merge. | `2026-10-15` |

Feature flags:

| Flag | Meaning | Criteria that need it today |
|---|---|---|
| `fine-granular-api` | ReadDataElement: `GET {api_base}/dpps/{dppId}/elements/{elementIdPath}` (EN 18222 6.1) | DPP-API-021 |
| `write-api` | Create and update passports (UpdateDPPById, …) | DPP-API-016 (needs credentials, not run yet) |
| `historical-versions` | ReadDPPVersionByIdAndDate (EN 18222 4.4) | DPP-API-019; DPP-STO-015 (with `backup-provider`) |
| `access-levels` | Controlled data elements that only authorised roles receive | DPP-ACC-006, DPP-ACC-012, DPP-STO-017; DPP-ACC-003 (needs credentials, not run yet); DPP-ACC-008, DPP-ACC-014 (self-declared) |
| `backup-provider` | The service acts as backup DPP service provider | DPP-STO-019; DPP-STO-015 (with `historical-versions`) |
| `registry-integration` | Registration with the EU DPP registry | – |
| `battery` | Battery passports | DPP-BAT-004 (with `access-levels`, needs credentials, not run yet) |
| `pcds` | Product circularity data sheets (ISO 59040) in passports | – |

Example of a self-declaration:

```yaml
declarations:
  - criterion: DPP-OPS-006
    statement: Test and production environments are separated.
    evidence: https://www.example.org/dpp/operations
```

## 4. Check your entry locally

Run dpp-validator against your entry before you open the pull request. The
image is built locally from the dpp-validator repository.

```sh
git clone https://github.com/OwnYourData/dpp-validator.git
cd dpp-validator
./build.sh
mkdir -p local
cp /path/to/example-dpp-service.yaml local/
docker run --rm -v "$PWD/local:/app/local" oydeu/dpp-validator:latest run --service local/example-dpp-service.yaml --output local/result.json
```

The first lines show the summary, for example
`12 of 13 automated checks passed (active criteria)`, followed by one line per
criterion with the reason of every failure or skip. The full result is in
`local/result.json`.

The run fails with exit code 2 and names the problem if the entry does not
match the schema. To try the entry without the write requests of section 2,
add `--read-only`; criteria with such requests are then reported as
`not_sent`.

The check needs a direct connection to your service: TLS and HTTP version
checks are meaningless behind a proxy that terminates TLS.

## 5. Open the pull request

1. Fork <https://github.com/OwnYourData/dpp-criteria> on GitHub (button
   **Fork**).
2. Clone your fork and create a branch:

   ```sh
   git clone https://github.com/<your-account>/dpp-criteria.git
   cd dpp-criteria
   git switch -c add-example-dpp-service
   ```

3. Add your entry as `services/<id>.yaml`.
4. Check it against the schema, as the CI does:

   ```sh
   python3 -m venv /tmp/dppc-venv
   /tmp/dppc-venv/bin/pip install -q check-jsonschema==0.29.4
   /tmp/dppc-venv/bin/check-jsonschema --schemafile schema/service.schema.json services/*.yaml
   ```

   Expected: `ok -- validation done`.
5. Commit and push:

   ```sh
   git add services/example-dpp-service.yaml
   git commit -m "Add Example DPP Service"
   git push -u origin add-example-dpp-service
   ```

6. Open the pull request against `main` of OwnYourData/dpp-criteria. Please
   use this text and complete it:

   ```markdown
   Adds <name of the service> to the daily checks.

   - Operator: <legal name>
   - Contact for questions about the results: <e-mail address>
   - Test passport: <productId>; it stays online while the service is listed.
   - Local run of dpp-validator on <date>: <N of M automated checks passed>

   I am authorised by the operator to list this service and agree that the
   daily run sends the requests described in services/README.md, including
   write requests without credentials that the service refuses.
   ```

   If you are not the operator, link the operator's written consent in the
   field `consent` and in the pull request.

The CI checks the schema and that the file name matches the `id`. A maintainer
reviews the entry, may ask questions in the pull request and merges it.

## 6. After the merge

- The service is part of the next daily run and appears on
  <https://ownyourdata.github.io/dpp-validator/>, with a link to the full JSON
  result. Earlier results stay on the branch `results` of dpp-validator.
- Every criterion on the results page links to its description; failures and
  warnings name the step and what was expected.
- **Changes** (new API base, other test passport, new features): a pull
  request that changes your file.
- **Removal**: a pull request that deletes your file, or a message to the
  maintainers. Results of earlier days stay in the history.
- New or changed criteria enter as `proposed` and are shown, but not counted,
  until a maintainer activates them.

## 7. Entries from our research

Entries with `entry.source: research` describe services we found in our own
research, from public information such as web pages, documentation, source
code and public demo instances. `entry.as_of` says when we last checked the
information. Such an entry:

- has no `contact`, `credentials`, `declarations` or `consent`, and `test_data`
  only if a public test passport is known;
- is checked with `check.mode: read-only-weekly`: once a week, only `GET`,
  `HEAD` and `OPTIONS` requests and no write requests, fewer than 30 requests
  per run (criteria that need other methods are reported as `not_sent`); or,
  for open software without a public instance, with
  `check.mode: test-instance-weekly`: once a week in full on a short-lived test
  instance of our own, started with the current release as published in
  `test_instance.setup` and discarded after the run; certificate, TLS and HTTP
  version checks and the criteria under `test_instance.not_applicable` are then
  reported as `not_applicable`, because they would describe our test
  environment; or with `check.mode: none` and a `check.reason`:
  `needs_credentials` (the EN 18222 paths answer only with credentials),
  `no_public_instance` (software without a public instance) or
  `no_en18222_paths` (no EN 18222 paths found);
- has its `example_passports` checked with dpplint once a week.

We would be very glad to hear from operators:

- **Correct an entry**: open an issue or a pull request that changes the file.
- **Take it over**: a pull request by the operator that sets
  `entry.source: operator` and adds the fields of section 3 (contact, test
  passport, …). From then on the service is checked in full every day.
- **Remove it**: open an issue or write to office@ownyourdata.eu; we remove
  the entry.

## 8. Questions

Open an issue in this repository or write to office@ownyourdata.eu.
