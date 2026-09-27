# DPP criteria

Open, community-maintained criteria for testing Digital Product Passport (DPP)
services and published passports against EU regulation and the harmonised
standards EN 18216, EN 18219, EN 18220, EN 18221, EN 18222 and EN 18223.

- `criteria/` – one YAML file per criterion
- `services/` – one YAML file per listed DPP service
- `soya/` – SOyA structures with the SHACL shapes of the passport checks, see [soya/README.md](soya/README.md)
- `tests/soya/` – test vectors for the structures
- `tests/schema/` – valid and invalid examples for the JSON Schemas
- `schema/` – JSON Schemas for both file types
- `scripts/` – build and test the structures with the SOyA web-cli, run the schema test vectors

The format is described in [CRITERIA-FORMAT.md](CRITERIA-FORMAT.md).

## Contributing

Propose a new or changed criterion with a pull request. New criteria enter
with `status: proposed`; a maintainer sets them to `active` after review.
Statements paraphrase their source – do not paste text from licensed standards.

A DPP service is listed only by a pull request from its operator, or with the
operator's consent linked in the pull request.

## What results mean

Results state how many automated checks a service passed on a given day and
which self-declarations it made. They are not a certification and do not
establish a presumption of conformity.

## License

Apache License 2.0 – see [LICENSE](LICENSE). This covers the criteria, schemas,
shapes and workflow files in this repository.
