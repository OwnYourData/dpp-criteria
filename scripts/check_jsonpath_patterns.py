"""Checks every JSONPath in the criteria (CRITERIA-FORMAT.md, "Regular expressions").

For each JSON assertion path (http steps, resolve expect and further_requests,
applies_if):

- placeholders may stand only inside string literals; they are replaced by
  "x" before parsing ("Placeholders in checks");
- the path must be valid RFC 9535 (jsonpath-rfc9535);
- every literal pattern of match() and search() must be valid I-Regexp
  (iregexp-check) and must not contain an unescaped ^ or $ outside a
  character class.

Usage: python3 scripts/check_jsonpath_patterns.py [file ...]
Needs: pip install jsonpath-rfc9535 iregexp-check pyyaml
"""

import glob
import re
import sys

import jsonpath_rfc9535
import yaml
from iregexp_check import check as iregexp_valid

PLACEHOLDER = re.compile(r"\{(base|dppId|productId|elementIdPath|randomId|now)\}")


def literals(path):
    """(start, end, quote, raw content) of every string literal in the path."""
    out, i, n = [], 0, len(path)
    while i < n:
        if path[i] in "'\"":
            quote, start, i = path[i], i, i + 1
            while i < n and path[i] != quote:
                i += 2 if path[i] == "\\" else 1
            out.append((start, i + 1, quote, path[start + 1:i]))
        i += 1
    return out


def unescape(raw):
    """Decodes the escapes of an RFC 9535 string literal."""
    simple = {"b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "/": "/", "\\": "\\", "'": "'", '"': '"'}
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c == "\\" and i + 1 < len(raw):
            e = raw[i + 1]
            if e == "u":
                out.append(chr(int(raw[i + 2:i + 6], 16)))
                i += 6
                continue
            out.append(simple.get(e, e))
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def substitute(path):
    """Replaces placeholders inside literals by x; returns (path, problem)."""
    spans = [(s, e) for s, e, _, _ in literals(path)]
    for m in PLACEHOLDER.finditer(path):
        if not any(s < m.start() and m.end() < e for s, e in spans):
            return path, f"placeholder {m.group(0)} outside a string literal"
    return PLACEHOLDER.sub("x", path), None


def function_patterns(path):
    """Literal second arguments of match() and search()."""
    found = []
    lits = literals(path)
    for m in re.finditer(r"\b(match|search)\s*\(", path):
        depth, i = 0, m.end()
        while i < len(path):
            lit = next((l for l in lits if l[0] == i), None)
            if lit:
                i = lit[1]
                continue
            c = path[i]
            if c in "([":
                depth += 1
            elif c in ")]":
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                j = i + 1
                while j < len(path) and path[j] == " ":
                    j += 1
                lit = next((l for l in lits if l[0] == j), None)
                if lit:
                    found.append((m.group(1), unescape(lit[3])))
                break
            i += 1
    return found


def anchor_problem(pattern):
    """An unescaped ^ or $ outside a character class, or None."""
    i, in_class = 0, False
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            i += 2
            continue
        if in_class:
            if c == "]":
                in_class = False
        elif c == "[":
            in_class = True
            if pattern[i + 1:i + 2] == "^":
                i += 1
        elif c in "^$":
            return f"unescaped {c} outside a character class"
        i += 1
    return None


def paths(doc):
    check = doc.get("check") or {}
    expects = [s.get("expect") or {} for s in check.get("steps") or []]
    expects.append(check.get("expect") or {})
    expects += [r.get("expect") or {} for r in check.get("further_requests") or []]
    for e in expects:
        for a in e.get("json") or []:
            yield a.get("path")
    for a in doc.get("applies_if") or []:
        yield a.get("path")


def problems(path):
    expanded, problem = substitute(path)
    if problem:
        return [problem]
    try:
        jsonpath_rfc9535.compile(expanded)
    except Exception as e:  # noqa: BLE001 - any parse error is a finding
        return [f"not valid RFC 9535: {str(e).splitlines()[0]}"]
    out = []
    for name, pattern in function_patterns(expanded):
        if not iregexp_valid(pattern):
            out.append(f"{name}() pattern {pattern!r} is not valid I-Regexp")
        elif (reason := anchor_problem(pattern)):
            out.append(f"{name}() pattern {pattern!r}: {reason}")
    return out


def main(files):
    failures = 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        for p in paths(doc):
            if not p:
                continue
            for problem in problems(p):
                print(f"::error file={f}::{p}: {problem}")
                failures += 1
    print(f"{len(files)} files checked, {failures} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or sorted(glob.glob("criteria/*/*.yaml"))))
