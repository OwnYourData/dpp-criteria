#!/bin/sh
# Runs the JSONPath test vectors in tests/jsonpath/:
#
#   valid/    scripts/check_jsonpath_patterns.py must accept every file
#   invalid/  it must reject each file on its own
#
# Needs jsonpath-rfc9535, iregexp-check and pyyaml, as in CI.
set -u
cd "$(dirname "$0")/.."
failures=0
for f in tests/jsonpath/valid/*.yaml; do
  if python3 scripts/check_jsonpath_patterns.py "$f" >/dev/null; then
    echo "ok   $f"
  else
    echo "FAIL $f (expected valid)"
    python3 scripts/check_jsonpath_patterns.py "$f"
    failures=$((failures + 1))
  fi
done
for f in tests/jsonpath/invalid/*.yaml; do
  if python3 scripts/check_jsonpath_patterns.py "$f" >/dev/null; then
    echo "FAIL $f (expected invalid)"
    failures=$((failures + 1))
  else
    echo "ok   $f"
  fi
done
[ "$failures" -eq 0 ] || { echo "$failures failure(s)"; exit 1; }
