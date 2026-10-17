# DPP criteria

Open, community-maintained criteria for testing Digital Product Passport (DPP)
services and published passports against EU regulation and the harmonised
standards EN 18216, EN 18219, EN 18220, EN 18221, EN 18222 and EN 18223.

- `criteria/` – one YAML file per criterion; [criteria/README.md](criteria/README.md) lists them all in readable form
- `services/` – one YAML file per listed DPP service
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

Propose a new or changed criterion with a pull request. New criteria enter
with `status: proposed`; a maintainer sets them to `active` after review.
Statements paraphrase their source – do not paste text from licensed standards.
After changing a criterion, run `python3 scripts/render_criteria_md.py` (needs
`pip install pyyaml`) and commit the updated `criteria/README.md`; CI checks
that it matches the YAML files.

A DPP service is listed only by a pull request from its operator, or with the
operator's consent linked in the pull request. How to add a service to the
daily checks, step by step: [services/README.md](services/README.md).

## What results mean

Results state how many automated checks a service passed on a given day and
which self-declarations it made. They are not a certification and do not
establish a presumption of conformity. Criteria that were not checked are
listed as `skipped` with a reason code, e.g. `not_applicable` or
`not_implemented` (see "Results" in [CRITERIA-FORMAT.md](CRITERIA-FORMAT.md)),
and never count.

## Funding

<!-- funding:begin -->
The DPP criteria catalogue is part of [PACE-DPP](https://dpp-austria.at/) – Promoting and Accelerating a Digital Product Passport based Data-Service Ecosystem. This Lighthouse Project has been made possible by financial contributions from the Austrian Federal Ministry of Innovation, Mobility and Infrastructure ([BMIMI](https://www.bmimi.gv.at/en.html), formerly BMK), supported by the Austrian Research Promotion Agency (FFG) under grant number [917177](https://projekte.ffg.at/projekt/5128301), as well as from the German Federal Ministry of Research, Technology and Space (BMFTR, formerly BMWK), supported by the German Research Promotion Agency (DLR-PT).
<!-- funding:end -->

## License

Apache License 2.0 – see [LICENSE](LICENSE). This covers the criteria, schemas,
shapes and workflow files in this repository.

The battery data points in `datapoints/batt/` follow the numbering and data
points of the European Commission's Guidance Document: Digital Batteries
Passport – data points by category, version 2.0 of 15 August 2026,
© European Union, 2026, reused under the
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence. Changes:
names and descriptions paraphrased, applicability expressed in a structured
field, access and granularity added from Regulation (EU) 2023/1542.
