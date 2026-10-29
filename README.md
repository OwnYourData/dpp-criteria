# DPP criteria

Open, community-maintained criteria for testing Digital Product Passport (DPP)
services and published passports against EU regulation and the harmonised
standards EN 18216, EN 18219, EN 18220, EN 18221, EN 18222 and EN 18223.

- `criteria/` – one YAML file per criterion; [criteria/README.md](criteria/README.md) lists them all in readable form
- `services/` – one YAML file per DPP service in the list, maintained by its operator or from our own research
- `datapoints/` – one YAML file per data point that EU legal acts require or allow in a passport (ESPR, toy safety, construction products, EUDR, batteries); [datapoints/README.md](datapoints/README.md) lists them all in readable form
- `soya/` – SOyA structures with the SHACL shapes of the passport checks, see [soya/README.md](soya/README.md)
- `tests/soya/` – test vectors for the structures
- `tests/schema/` – valid and invalid examples for the JSON Schemas
- `schema/` – JSON Schemas for the three file types
- `scripts/` – build and test the structures with the SOyA web-cli, run the schema test vectors, render `criteria/README.md`, `datapoints/README.md` and the funding notice in this README
- `config/funding.yml` – the funding notice, the one place where its wording is kept

The format is described in [CRITERIA-FORMAT.md](CRITERIA-FORMAT.md), the data
point format in [DATAPOINT-FORMAT.md](DATAPOINT-FORMAT.md).

## Contributing

Propose a new or changed criterion, data point or service entry with an issue
or a pull request; [CONTRIBUTING.md](CONTRIBUTING.md) explains the steps. New
criteria enter with `status: proposed`; a maintainer sets them to `active`
after review. Statements paraphrase their source – do not paste text from
licensed standards.

DPP services are listed in two ways. An operator adds its service by pull
request, or someone adds it with the operator's consent linked in the pull
request; these services are checked in full every day. We also list services
we found in our own research. These entries are marked as our own research,
are checked read-only at most once a week, and may be incomplete or out of
date. Open software without a public instance is checked once a week in full
on a short-lived test instance of our own, started with the current release
and discarded after the run. We would be very glad to hear from operators: a pull request or an issue
can correct an entry or turn it into an operator entry, and on request we
remove a research entry. How to add or correct a service, step by step:
[services/README.md](services/README.md).

## What results mean

This repository is part of a research project. It shares what we currently
know about DPP standards and services. It makes no claim to be complete and is
not a legal assessment.

Results state how many automated checks a service passed on a given day and
which self-declarations it made. They are not a certification and do not
establish a presumption of conformity. Criteria that were not checked are
listed as `skipped` with a reason code, e.g. `not_applicable` or
`not_implemented` (see "Results" in [CRITERIA-FORMAT.md](CRITERIA-FORMAT.md)),
and never count.

## Related tools

These repositories and services of OwnYourData belong together. Each is a
project of its own; the list shows how they depend on each other.

- **dpp-criteria** (this repository) – the criteria, the SOyA structures of
  the passport checks, the data points and the list of services.
- [dpplint](https://github.com/OwnYourData/dpplint) – checks the passport
  behind a product identifier against the passport criteria of this
  repository, at <https://dpplint.ownyourdata.eu>. Its image contains the
  criteria and structures of a fixed commit of this repository.
- [dpp-validator](https://github.com/OwnYourData/dpp-validator) – runs the
  service criteria of this repository against the listed services and checks
  their example passports with dpplint; results at
  <https://ownyourdata.github.io/dpp-validator/>. It reads this repository at
  the commit pinned in its `DPP_CRITERIA_REF`.
- [DIDlint](https://github.com/OwnYourData/didlint) – validates DID
  documents, at <https://didlint.ownyourdata.eu>; dpplint calls it for the
  DIDs in a passport (DPP-ID-016).
- [SOyA](https://ownyourdata.github.io/soya/)
  ([source](https://github.com/OwnYourData/soya)) – the structures in `soya/`
  are SOyA structures; dpplint validates passports with the SOyA web-cli.
- [OYDID](https://ownyourdata.github.io/oydid/)
  ([source](https://github.com/OwnYourData/oydid)) – the DID method
  `did:oyd`; DIDlint resolves `did:oyd` through the OYDID resolver.

OwnYourData also operates the OwnYourData DPP Service, which is one of the
listed services (`services/ownyourdata-dpp-service.yaml`) and goes through the
same checks as every other entry.

## Funding

<!-- funding:begin -->
The DPP criteria catalogue is part of [PACE-DPP](https://dpp-austria.at/) – Promoting and Accelerating a Digital Product Passport based Data-Service Ecosystem. This Lighthouse Project has been made possible by financial contributions from the Austrian Federal Ministry of Innovation, Mobility and Infrastructure ([BMIMI](https://www.bmimi.gv.at/en.html), formerly BMK), supported by the Austrian Research Promotion Agency (FFG) under grant number [917177](https://projekte.ffg.at/projekt/5128301), as well as from the German Federal Ministry of Research, Technology and Space (BMFTR, formerly BMWK), supported by the German Research Promotion Agency (DLR-PT).
<!-- funding:end -->

## License

This repository has a mixed licence. [NOTICE](NOTICE) lists for each folder
which licence applies and gives the attribution for the material reused from
third parties.

| Path | Licence |
|---|---|
| `criteria/`, `schema/`, `services/`, `soya/`, `scripts/`, `tests/`, `config/`, documentation | [Apache License 2.0](LICENSE) |
| `datapoints/espr/`, `datapoints/cpr/`, `datapoints/toy/`, `datapoints/eudr/`, the other sections of `datapoints/README.md` | [Apache License 2.0](LICENSE), except the `semantic_ids` from IDTA |
| `datapoints/batt/` and its section in `datapoints/README.md` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), adapted from the European Commission's battery passport guidance |
| `semantic_ids` with `scheme: idta-cds` (all data points) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), from the IDTA submodel templates |
| `semantic_ids` with `scheme: iec-cdd` | free attributes of the IEC Common Data Dictionary, source: IEC |

The battery data points in `datapoints/batt/` follow the numbering and data
points of the European Commission's Guidance Document: Digital Batteries
Passport – data points by category, version 2.0 of 15 August 2026,
© European Union, 2026, reused under the
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence. Changes:
names and descriptions paraphrased, applicability expressed in a structured
field, access and granularity added from Regulation (EU) 2023/1542.

The semantic identifiers of the data points (`semantic_ids`) come from:

- the submodel templates that the Industrial Digital Twin Association (IDTA)
  publishes in [admin-shell-io/submodel-templates](https://github.com/admin-shell-io/submodel-templates)
  under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence. Each
  entry names the template and version in `source`. Only the identifiers and
  their `isCaseOf` relations are taken over, no names or definitions;
- the IEC Common Data Dictionary (IEC 61360), source: IEC. The IRDIs are
  taken as named in the IDTA templates; they are free attributes under the
  [licence of the IEC CDD](https://cdd.iec.ch/CDD/iec61360/iec61360.nsf/License),
  section 5.

Contributions are accepted under the licence of the folder they change, see
[CONTRIBUTING.md](CONTRIBUTING.md#10-licence-of-contributions).
