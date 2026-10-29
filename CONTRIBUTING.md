# Contributing

Thank you for helping to improve the DPP criteria. Contributions are welcome
from anyone: operators of DPP services, implementers, people who work with the
standards and the legal acts, and users of dpplint and dpp-validator.

This repository is part of a research project. It shares what we currently
know about DPP standards and services, makes no claim to be complete and is not
a legal assessment. The same holds for contributions: a criterion records how
we read a source and how we check it, not an authoritative interpretation.

## Contents

1. [Ways to contribute](#1-ways-to-contribute)
2. [Propose a new criterion](#2-propose-a-new-criterion)
3. [Change a criterion](#3-change-a-criterion)
4. [Self-declarations](#4-self-declarations)
5. [Service entries](#5-service-entries)
6. [Data points](#6-data-points)
7. [Tests and CI](#7-tests-and-ci)
8. [From proposed to active](#8-from-proposed-to-active)
9. [Where results appear](#9-where-results-appear)
10. [Licence of contributions](#10-licence-of-contributions)
11. [Rules for all texts](#11-rules-for-all-texts)

## 1. Ways to contribute

- **Open an issue** to report a wrong or missing criterion, a false result of
  dpplint or dpp-validator, or a source we should look at. Please name the
  criterion ID, the source and clause, and if possible a product identifier or
  service where the problem shows.
- **Open a pull request** with a new or changed criterion, data point or
  service entry. One criterion, data point or service per file keeps pull
  requests small; please keep one topic per pull request.

For larger changes (a new area, a new check type, a change to a schema) please
open an issue first, so that we can agree on the approach before you write it.

## 2. Propose a new criterion

1. Check [criteria/README.md](criteria/README.md): the requirement may already
   be covered, possibly by a criterion that several catalogue rows share.
2. Find the source. A criterion rests on at least one `basis` entry with the
   clause it paraphrases: an EU legal act, a published standard, or published
   guidance. Use the published editions; a draft (prEN, FprEN) is
   `kind: draft-standard` and does not support a presumption of conformity.
   `kind: derived` (an engineering inference from the other entries) can never
   be the only basis of a `MUST`.
3. Create `criteria/<area>/DPP-<AREA>-<NNN>.yaml` with the next free number in
   its area, `version: 1` and `status: proposed`. The fields and check types
   are described in [CRITERIA-FORMAT.md](CRITERIA-FORMAT.md):
   - `statement`: one English sentence with an RFC 2119 keyword in capitals,
     paraphrasing the source;
   - `target`: `passport` (checked by dpplint on a published passport),
     `service` (checked by dpp-validator on a listed service) or `operator`
     (only with `method: self-declared`);
   - `method`: `automated`, `automated-auth` (needs test credentials from the
     operator) or `self-declared`;
   - `check`: one of the check types of CRITERIA-FORMAT.md. A check that needs
     a new type also needs it in the runner (dpplint or dpp-validator); please
     open an issue first.
4. For a passport check with `check.type: shacl`, add or extend the SOyA
   structure in [soya/](soya/README.md) and add test vectors in `tests/soya/`
   that pass and fail as expected.
5. Run `python3 scripts/render_criteria_md.py` (needs `pip install pyyaml`)
   and commit the updated `criteria/README.md`.
6. Run the checks of [section 7](#7-tests-and-ci) and open the pull request.
   In its description, say what the criterion checks, which source it rests
   on and how you tested it.

## 3. Change a criterion

- Change the YAML file and render `criteria/README.md` again.
- Bump `version` when the statement, level, basis or check changes meaning.
  Typos and wording that keeps the meaning do not bump it.
- A criterion that should no longer apply is set to `status: deprecated`, not
  deleted. Its ID is never reused.
- A change to an `active` criterion changes published results. Please say in
  the pull request how results of the listed services change, if you know.

## 4. Self-declarations

Some requirements cannot be checked from the outside, for example how a
service logs access to controlled data. Such criteria have
`method: self-declared` and `check.type: declaration`.

An operator declares them in its service entry under `declarations`: the
criterion, a statement and an `https://` link to evidence (see
[services/README.md](services/README.md#3-the-service-entry)). Results list
self-declarations separately, with the statement and the link as given. They
are not checked and never count as passed.

## 5. Service entries

Every listed DPP service is one file `services/<id>.yaml`.
[services/README.md](services/README.md) explains step by step how an operator
adds its service, which requests the daily run sends, and how an operator
corrects, takes over or removes an entry from our own research. Someone who is
not the operator links the operator's written consent in the field `consent`
and in the pull request.

## 6. Data points

Data points that EU legal acts require or allow in a passport are one file
each under `datapoints/<regime>/`, in the format of
[DATAPOINT-FORMAT.md](DATAPOINT-FORMAT.md). After a change, run
`python3 scripts/render_datapoints_md.py` and commit the updated
`datapoints/README.md`.

`semantic_ids` list identifiers of open dictionaries only when a published
document ties them to the data point; a similar name is not enough. Only the
identifier is given, never names or definitions from the dictionary. The
scheme `eclass` is reserved and rejected by the schema.

## 7. Tests and CI

Every pull request runs the workflow `validate` with four jobs:

| Job | What it checks |
|---|---|
| `schema` | criteria, service entries and data points against the JSON Schemas in `schema/`; the schema test vectors in `tests/schema/`; file names match the `id` |
| `jsonpath` | JSONPath expressions and the patterns of `match()`/`search()` in the criteria, with their test vectors |
| `catalogue` | `criteria/README.md`, `datapoints/README.md` and the funding notice in `README.md` match their sources |
| `structures` | the SOyA structures against the test vectors in `tests/soya/`, in the same SOyA image that dpplint uses |

The same checks locally (Python 3.12; Docker for the structures):

```sh
python3 -m venv /tmp/dppc-venv
/tmp/dppc-venv/bin/pip install -q check-jsonschema==0.29.4 jsonpath-rfc9535==2.0.0 iregexp-check==0.1.4 pyyaml==6.0.2
PATH="/tmp/dppc-venv/bin:$PATH"
check-jsonschema --schemafile schema/criterion.schema.json criteria/*/*.yaml
check-jsonschema --schemafile schema/service.schema.json services/*.yaml
check-jsonschema --schemafile schema/datapoint.schema.json datapoints/*/*.yaml
sh scripts/test_schema.sh
python3 scripts/check_jsonpath_patterns.py
sh scripts/test_jsonpath_patterns.sh
python3 scripts/render_criteria_md.py --check
python3 scripts/render_datapoints_md.py --check
python3 scripts/render_funding_md.py --check
sh scripts/run_structure_tests.sh
```

A check of a service entry against the live service is described in
[services/README.md](services/README.md#4-check-your-entry-locally).

## 8. From proposed to active

1. A maintainer reviews the pull request: source and clause, paraphrase,
   check, tests. The criterion is merged with `status: proposed`.
2. The maintainers update dpplint and dpp-validator to the new commit of this
   repository. From the next run on, the criterion is checked and shown in the
   results, marked as proposed and not counted.
3. Once it has run against the listed services and passports and its results
   have been reviewed, a maintainer sets it to `active` in a pull request of
   its own. From then on it counts in "N of M automated checks passed".

Criteria with `automated-auth` are listed as skipped until the runners can use
test credentials; self-declared criteria are listed but never counted.

## 9. Where results appear

- **dpplint**: <https://dpplint.ownyourdata.eu> checks any product identifier
  on request, as a web page and through its API.
- **dpp-validator**: <https://ownyourdata.github.io/dpp-validator/> shows the
  latest results of every listed service and its example passports, with
  `available-services.json` for machines. The JSON results of every run are
  kept on the branch `results` of
  [dpp-validator](https://github.com/OwnYourData/dpp-validator).
- Every result names the commit of this repository it was produced with and
  links to the description of each criterion.

## 10. Licence of contributions

By opening a pull request you confirm that you may contribute its content, and
you agree that it is licensed under the licence of the folder it changes (see
[NOTICE](NOTICE) and "License" in [README.md](README.md#license)):

- the Apache License 2.0 for criteria, schemas, structures, service entries,
  scripts, tests, documentation and the data points outside `datapoints/batt/`;
- CC BY 4.0 for changes to `datapoints/batt/` and to `semantic_ids` taken from
  IDTA submodel templates, which are adapted from material under that licence.

Do not add material from third parties unless its licence allows reuse under
these terms, and name the source. Never add text from licensed standards (EN,
ISO, IEC and others) or content of licensed dictionaries such as ECLASS.

## 11. Rules for all texts

- Paraphrase sources and cite the clause; do not quote licensed standards.
- Results say how many automated checks passed and which self-declarations
  were made. Never describe a service or passport as conformant or as
  certified, and do not claim completeness or legal correctness.
- Describe the current state; the history of a file is in Git.
- Do not put secrets, credentials or personal data into the repository.
