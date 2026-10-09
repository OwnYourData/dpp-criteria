# Adding a DPP service to the daily checks

This guide explains how the operator of a Digital Product Passport (DPP)
service adds the service to the list checked every day by
[dpp-validator](https://github.com/OwnYourData/dpp-validator). The results
are published at <https://ownyourdata.github.io/dpp-validator/>.

Results are results of automated checks only. They are no certification and
establish no presumption of conformity.

## Contents

1. [What is checked](#1-what-is-checked)
2. [Before you start](#2-before-you-start)
3. [The service entry](#3-the-service-entry)
4. [Check your entry locally](#4-check-your-entry-locally)
5. [Open the pull request](#5-open-the-pull-request)
6. [After the merge](#6-after-the-merge)
7. [Questions](#7-questions)

## 1. What is checked

Every day at about 04:17 UTC, dpp-validator runs all service criteria of this
repository (`target: service`, `method: automated`) against every service
listed in this directory. Examples:

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
operator:
  name: Example GmbH
  url: https://www.example.org
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
| `operator.name` | yes | Legal name of the operator. | `Example GmbH` |
| `operator.url` | no | Website of the operator. | `https://www.example.org` |
| `contact` | yes | E-mail address for questions about the results; shown as a mailto link. | `dpp@example.org` |
| `api_base` | yes | Base URL of the EN 18222 API, `https://`, ending with the version prefix `v1`. The criteria append paths such as `/dpps/{dppId}`. | `https://dpp.example.org/api/v1` |
| `features` | yes | Optional parts of the standard the service offers (list below). An empty list `[]` is allowed. | `[fine-granular-api]` |
| `not_implemented` | no | Optional parts that concern the service but are not available yet. Their criteria are reported as `not_implemented` instead of `not_applicable`. A flag may not be in `features` and `not_implemented` at the same time. | `[write-api, historical-versions]` |
| `test_data.productId` | yes | Exactly the value of `uniqueProductIdentifier` in the test passport. Ideally an HTTPS URL that resolves to the passport (EN 18219). Used in `ReadDPPByProductId`. | `https://dpp.example.org/01/09520123456788/21/000001` |
| `test_data.dppId` | yes | Exactly the value of `digitalProductPassportId` in the test passport. Used in `ReadDPPById`; the run percent-encodes it in the path. | `https://dpp.example.org/dpp/000001` or `did:example:123` |
| `test_data.elementIdPath` | with `fine-granular-api` | RFC 9535 JSONPath of one data element of the test passport, in the compressed representation (EN 18223 5.2: element IDs as keys). | `$.ProductIdentification.ModelIdentifier` |
| `credentials` | yes | Always `none` for now: checks that need test credentials are not run yet. Never put secrets into this repository. | `none` |
| `declarations` | no | Self-declarations for criteria with `method: self-declared`, each with `criterion`, `statement` and an `evidence` URL. They are listed, never counted as passed. | see below |
| `consent` | if the PR is not opened by the operator | Link to the operator's written consent. | `https://github.com/OwnYourData/dpp-criteria/issues/42` |
| `listed_since` | yes | Date of the pull request (`YYYY-MM-DD`); the maintainers set the date of the merge. | `2026-10-15` |

Feature flags:

| Flag | Meaning | Criteria that need it today |
|---|---|---|
| `fine-granular-api` | ReadDataElement: `GET {api_base}/dpps/{dppId}/elements/{elementIdPath}` (EN 18222 6.1) | DPP-API-021 |
| `write-api` | Create and update passports (UpdateDPPById, …) | DPP-API-016 (needs credentials, not run yet) |
| `historical-versions` | ReadDPPVersionByIdAndDate (EN 18222 4.4) | DPP-API-019 |
| `access-levels` | Restricted data elements with access levels | – |
| `backup-provider` | The service acts as backup DPP service provider | – |
| `registry-integration` | Registration with the EU DPP registry | – |
| `battery` | Battery passports | – |
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

## 7. Questions

Open an issue in this repository or write to office@ownyourdata.eu.
