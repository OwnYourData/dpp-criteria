#!/bin/sh
# Runs the schema test vectors in tests/schema/<schema>/:
#
#   valid/    every file must validate against schema/<schema>.schema.json
#   invalid/  every file must be rejected by it (each file on its own)
#
# Needs check-jsonschema (pip install check-jsonschema), as in CI.
set -u
cd "$(dirname "$0")/.."
failures=0
for dir in tests/schema/*/; do
  name=$(basename "$dir")
  schema="schema/$name.schema.json"
  for f in "$dir"valid/*.yaml; do
    [ -e "$f" ] || continue
    if check-jsonschema --schemafile "$schema" "$f" >/dev/null 2>&1; then
      echo "ok   $f"
    else
      echo "FAIL $f (expected valid)"
      check-jsonschema --schemafile "$schema" "$f"
      failures=$((failures + 1))
    fi
  done
  for f in "$dir"invalid/*.yaml; do
    [ -e "$f" ] || continue
    if check-jsonschema --schemafile "$schema" "$f" >/dev/null 2>&1; then
      echo "FAIL $f (expected invalid)"
      failures=$((failures + 1))
    else
      echo "ok   $f"
    fi
  done
done
[ "$failures" -eq 0 ] || { echo "$failures schema test vector(s) failed"; exit 1; }
