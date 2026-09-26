"""Run the SHACL shapes in shapes/ against the test vectors in tests/shapes/.

tests/shapes/<shape>/valid/*.json    must pass without results
tests/shapes/<shape>/warning/*.json  must pass with at least one warning
tests/shapes/<shape>/invalid/*.json  must fail with at least one violation
"""
import json
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parent.parent
SH = Namespace("http://www.w3.org/ns/shacl#")
CONTEXT = json.loads((ROOT / "shapes" / "en18223-context.jsonld").read_text())["@context"]


def to_graph(passport):
    doc = {"@context": CONTEXT, "@type": "DigitalProductPassport", **passport}
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld")
    return g


def run(shapes_file, vector):
    data = to_graph(json.loads(vector.read_text()))
    _, report, text = validate(data, shacl_graph=str(shapes_file), shacl_graph_format="turtle", allow_warnings=True)
    if not isinstance(report, Graph):
        raise SystemExit(f"{shapes_file.name}: {text}")
    counts = {"violation": 0, "warning": 0, "info": 0}
    messages = []
    for result in report.subjects(RDF.type, SH.ValidationResult):
        severity = report.value(result, SH.resultSeverity)
        key = {SH.Violation: "violation", SH.Warning: "warning", SH.Info: "info"}[severity]
        counts[key] += 1
        messages.append(f"{key}: {report.value(result, SH.resultMessage)}")
    return counts, messages


def main():
    failures = 0
    for shape_dir in sorted((ROOT / "tests" / "shapes").iterdir()):
        shapes_file = ROOT / "shapes" / f"{shape_dir.name}.ttl"
        for expected in ("valid", "warning", "invalid"):
            for vector in sorted((shape_dir / expected).glob("*.json")):
                counts, messages = run(shapes_file, vector)
                ok = {
                    "valid": counts["violation"] == 0 and counts["warning"] == 0,
                    "warning": counts["violation"] == 0 and counts["warning"] > 0,
                    "invalid": counts["violation"] > 0,
                }[expected]
                name = vector.relative_to(ROOT / "tests" / "shapes")
                print(f"{'ok  ' if ok else 'FAIL'} {name}  ({counts['violation']} violations, {counts['warning']} warnings)")
                if not ok:
                    failures += 1
                    for m in messages:
                        print(f"       {m}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
