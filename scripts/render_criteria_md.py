"""Renders the criteria as one human-readable Markdown page: criteria/README.md.

GitHub shows the page below the file list of the criteria/ folder. It is
generated from criteria/*/*.yaml and must not be edited by hand: change the
YAML file, run this script and commit both. CI runs it with --check.

Usage: python3 scripts/render_criteria_md.py [--check]
Needs: pip install pyyaml
"""

import glob
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "criteria", "README.md")

# Areas of the DPP System Requirements Katalog v2, in catalogue order.
AREAS = [
    ("Scope and configuration", ["CFG"]),
    ("Governance and roles", ["ROL"]),
    ("Identification", ["ID"]),
    ("Data carrier", ["CAR"]),
    ("DPP creation and validation", ["CRT"]),
    ("Data model and semantics", ["DAT"]),
    ("APIs and data exchange", ["API", "DEX"]),
    ("EU DPP registry and onboarding", ["REG"]),
    ("Access control", ["ACC"]),
    ("Security, integrity and privacy", ["SEC"]),
    ("Storage, backup and persistence", ["BCK", "STO"]),
    ("Lifecycle, transfer and audit", ["LCM"]),
    ("Interoperability and standards", ["INT"]),
    ("Enterprise integration and data quality", ["ENT", "DQ"]),
    ("Operations and change management", ["OPS"]),
    ("Product-specific: batteries", ["BAT"]),
    ("Circularity and environmental data", ["PCDS", "LCA", "EPD"]),
    ("Traceability and supply chain", ["TRC"]),
    ("Data governance and assurance", ["DGA"]),
    ("Sectoral compliance", ["EUDR"]),
]

STATUS_ORDER = ["active", "proposed", "deprecated"]

TARGET = {
    "passport": "published passport",
    "service": "DPP service",
    "operator": "economic operator",
}

METHOD = {
    "automated": "automated",
    "automated-auth": "automated, with test credentials",
    "self-declared": "self-declared",
}

KIND = {
    "regulation": "regulation",
    "harmonised-standard": "harmonised standard",
    "draft-standard": "draft standard",
    "standard": "standard",
    "guidance": "guidance",
    "derived": "derived",
}

TLS_VERSION = {"ssl3": "SSL 3.0", "1.0": "TLS 1.0", "1.1": "TLS 1.1",
               "1.2": "TLS 1.2", "1.3": "TLS 1.3"}

HTTP_VERSION = {"1.0": "HTTP/1.0", "1.1": "HTTP/1.1", "2": "HTTP/2", "3": "HTTP/3"}


# --- Markdown helpers -------------------------------------------------------

def text(s):
    """Prose from a YAML field, with Markdown syntax characters escaped."""
    s = " ".join(str(s).split())
    s = s.replace("\\", "\\\\")
    for ch in "*_`[]<>|":
        s = s.replace(ch, "\\" + ch)
    return s


def code(v):
    """Inline code; JSON for values that are not strings."""
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    fence = "``" if "`" in s else "`"
    pad = " " if s.startswith("`") or s.endswith("`") else ""
    return f"{fence}{pad}{s}{pad}{fence}"


def slug(heading):
    """Anchor GitHub generates for a heading."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def either(items, word="or"):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {word} " + items[-1]


# --- Check descriptions -----------------------------------------------------

def warn(a):
    return " (warning only)" if a.get("severity") == "warning" else ""


def json_assertion(a):
    p = code(a["path"])
    if "exists" in a:
        s = f"{p} exists" if a["exists"] else f"{p} does not exist"
    elif "equals" in a:
        s = f"{p} equals {code(a['equals'])}"
    elif "in" in a:
        s = f"{p} is one of {either(code(v) for v in a['in'])}"
    elif "matches" in a:
        s = f"{p} matches {code(a['matches'])}"
    else:
        s = p
    return s + warn(a)


def header_assertion(a):
    parts = []
    if "exists" in a:
        parts.append("is present" if a["exists"] else "is absent")
    if "equals" in a:
        parts.append(f"equals {code(a['equals'])}")
    if "contains" in a:
        parts.append(f"lists {code(a['contains'])}")
    if "matches" in a:
        parts.append(f"matches {code(a['matches'])}")
    return f"header {code(a['name'])} {either(parts, 'and')}" + warn(a)


def expectation(e):
    out = []
    if "status" in e:
        out.append("status " + either(str(s) for s in e["status"]))
    if "content_type" in e:
        out.append("content type " + code(e["content_type"]))
    out += [header_assertion(a) for a in e.get("headers", [])]
    out += [json_assertion(a) for a in e.get("json", [])]
    if "body_equals_step" in e:
        out.append(f"body identical to step {e['body_equals_step']}")
    return "; ".join(out) if out else "any answer"


def request_line(r):
    s = code(f"{r['method']} {r['path']}")
    extra = []
    if r.get("auth") == "token":
        extra.append("with the operator's test token")
    elif r.get("auth") == "none":
        extra.append("without credentials")
    for name, value in (r.get("headers") or {}).items():
        extra.append(f"header {code(f'{name}: {value}')}")
    if "body" in r:
        extra.append(f"body {code(r['body'])}")
    return s + (", " + ", ".join(extra) if extra else "")


def describe_http(c):
    lines = []
    if "base_matches" in c:
        lines.append(f"The API base of the service must match {code(c['base_matches'])}.")
    lines.append("Requests to the API base of the service, in this order:")
    lines.append("")
    for i, step in enumerate(c["steps"], 1):
        line = f"{i}. {request_line(step['request'])} → expect {expectation(step.get('expect', {}))}"
        if "skip_if_status" in step:
            line += "; status " + either(str(s) for s in step["skip_if_status"]) + " → skipped"
        if "warn_if_status" in step:
            line += "; status " + either(str(s) for s in step["warn_if_status"]) + " → warning"
        if step.get("severity") == "warning":
            line += " (a failure of this step gives only a warning)"
        lines.append(line)
    return lines


def describe_tls(c):
    lines = ["TLS and HTTP properties of the host of the API base:", ""]
    if c.get("valid_certificate"):
        lines.append("- the certificate chain and host name verify against the common public CA set")
    if c.get("https_redirect"):
        lines.append("- plain HTTP on port 80 serves nothing: it redirects to `https://`, "
                     "refuses the connection or answers with an error status")
    if "min_version" in c:
        lines.append(f"- at least {TLS_VERSION.get(c['min_version'], c['min_version'])} is negotiated")
    if c.get("reject_versions"):
        lines.append("- handshakes offering only "
                     + either(TLS_VERSION.get(v, v) for v in c["reject_versions"])
                     + " are refused")
    if c.get("recommend_versions"):
        lines.append("- " + either(TLS_VERSION.get(v, v) for v in c["recommend_versions"])
                     + " is offered (otherwise a warning)")
    hv = c.get("http_versions") or {}
    if hv.get("require"):
        lines.append("- " + either((HTTP_VERSION.get(v, v) for v in hv["require"]), "and")
                     + " is selected and answers successfully")
    if hv.get("reject"):
        lines.append("- requests forced to " + either(HTTP_VERSION.get(v, v) for v in hv["reject"])
                     + " get no successful (2xx/3xx) answer")
    return lines


def describe_shacl(c):
    if "structure" in c:
        name = c["structure"]
        ref = code(name)
        if os.path.exists(os.path.join(ROOT, "soya", name + ".yml")):
            ref = f"[{ref}](../soya/{name}.yml)"
        return [f"The passport fetched via the product identifier is validated against the "
                f"SHACL shapes of the SOyA structure {ref}; only the results tagged with this "
                f"criterion's ID count."]
    src = {
        "content-specification": "shapes chosen by the passport's `contentSpecificationIds`",
        "semantic-repository": "shapes from the European Commission's semantic repository",
    }.get(c.get("shapes_select"), code(c.get("shapes_select")))
    return [f"The passport fetched via the product identifier is validated against {src}. "
            f"If no shapes are found, the result is skipped."]


def describe_resolve(c):
    accept = f" with {code('Accept: ' + c['accept'])}" if "accept" in c else ""
    lines = [f"The product identifier is opened like a phone scanning the data carrier "
             f"(plain HTTPS GET{accept})."]
    if "expect" in c:
        lines[0] += f" Expected: {expectation(c['expect'])}."
    else:
        lines[0] += (" Expected: a single passport object whose `uniqueProductIdentifier` "
                     "equals the identifier.")
    for r in c.get("further_requests", []):
        line = (f"Further request with {code('Accept: ' + r['accept'])}: expect "
                f"{expectation(r.get('expect', {}))}")
        if r.get("severity") == "warning":
            line += " (warning only)"
        lines.append("- " + line + ".")
    if len(lines) > 1:
        lines.insert(1, "")
    h = c.get("history") or {}
    if "fail_after_consecutive_days" in h:
        lines += ["", f"Rated only from the validator's daily runs: fails after "
                      f"{h['fail_after_consecutive_days']} consecutive days without success."]
    return lines


def describe_did(c):
    paths = either((code(p) for p in c.get("paths", [])), "and")
    s = (f"The DIDs found at {paths} are resolved and checked against DID Core and DID "
         f"Resolution; values that are not DIDs are skipped.")
    if "vc_data_model" in c:
        s += f" Associated credentials are checked against the VC Data Model {c['vc_data_model']}."
    return [s]


def describe_proof(c):
    s = ("The integrity proofs of the passport are verified (formats: "
         + either((code(f) for f in c.get("formats", [])), "and") + "). Without a proof the "
         "result is skipped.")
    if "key_from" in c:
        s += (f" At least one verified proof must be issued with a key of the DID at "
              f"{code(c['key_from'])}; otherwise a warning.")
    return [s]


def describe_links(c):
    req = either((code(a) for a in c.get("required", [])), "and")
    s = (f"Every {code(c['element_type'])} element of the passport must have {req}, "
         f"and its URL must answer.")
    if c.get("unreachable") == "warning":
        s += " A URL that does not answer gives a warning."
    return [s]


def describe_declaration(c):
    return ["The service entry must contain a self-declaration for this criterion with a "
            "statement and an evidence URL. Only its presence and that the URL answers are "
            "checked; the result is shown separately and never as passed."]


DESCRIBE = {
    "http": describe_http,
    "tls": describe_tls,
    "shacl": describe_shacl,
    "resolve": describe_resolve,
    "did": describe_did,
    "proof": describe_proof,
    "links": describe_links,
    "declaration": describe_declaration,
}


# --- Page -------------------------------------------------------------------

def load():
    criteria = []
    for path in sorted(glob.glob(os.path.join(ROOT, "criteria", "*", "*.yaml"))):
        with open(path, encoding="utf-8") as f:
            c = yaml.safe_load(f)
        c["_file"] = os.path.relpath(path, os.path.join(ROOT, "criteria")).replace(os.sep, "/")
        criteria.append(c)
    return criteria


def area_of(c):
    return c["id"].split("-")[1]


def grouped(criteria):
    known = {code_: name for name, codes in AREAS for code_ in codes}
    groups = []
    for name, codes in AREAS:
        items = [c for c in criteria if area_of(c) in codes]
        if items:
            groups.append((name, sorted(items, key=lambda c: c["id"])))
    rest = sorted((c for c in criteria if area_of(c) not in known), key=lambda c: c["id"])
    if rest:
        groups.append(("Other areas", rest))
    return groups


def heading(c):
    return f"{c['id']}: {c['title']}"


def basis_line(b):
    src = text(b["source"])
    if b.get("url"):
        src = f"[{src}]({b['url']})"
    clause = f", {text(b['clause'])}" if b.get("clause") else ""
    return f"- {src}{clause} ({KIND.get(b['kind'], b['kind'])})"


def criterion_section(c):
    out = [f"### {text(heading(c))}", ""]
    out.append(" · ".join([
        f"**{c['level']}**",
        f"checked on: {TARGET.get(c['target'], c['target'])}",
        METHOD.get(c["method"], c["method"]),
        f"status: {c['status']}",
        f"version {c['version']}",
    ]))
    out += ["", "> " + text(c["statement"]), ""]

    out += ["**Basis**", ""]
    out += [basis_line(b) for b in c["basis"]]
    out.append("")

    conditions = []
    if c.get("requires_features"):
        conditions.append("the service declares the feature "
                          + either((code(f) for f in c["requires_features"]), "and"))
    if c.get("applies_if"):
        conditions.append("the passport meets: "
                          + "; ".join(json_assertion(a) for a in c["applies_if"])
                          + " (otherwise skipped)")
    if conditions:
        out += ["**Applies only if** " + "; ".join(conditions) + ".", ""]

    check = c.get("check") or {}
    describe = DESCRIBE.get(check.get("type"))
    if describe:
        lines = describe(check)
        out.append("**How it is checked** " + lines[0])
        out += lines[1:]
        out.append("")

    if c.get("notes"):
        out += ["**Notes** " + text(c["notes"]), ""]

    refs = c.get("catalogue_ref") or []
    refs = [refs] if isinstance(refs, str) else refs
    meta = []
    if refs:
        meta.append("Catalogue rows: " + ", ".join(refs))
    meta.append(f"Source: [{c['_file']}]({c['_file']})")
    out += [" · ".join(meta), ""]
    return out


def counts_table(criteria):
    statuses = [s for s in STATUS_ORDER if any(c["status"] == s for c in criteria)]
    out = ["| | " + " | ".join(statuses) + " | total |",
           "|---|" + "---:|" * (len(statuses) + 1)]

    def row(label, items):
        cells = [str(sum(1 for c in items if c["status"] == s)) for s in statuses]
        return f"| {label} | " + " | ".join(cells) + f" | {len(items)} |"

    for key, label in [("passport", "Published passport (dpplint)"),
                       ("service", "DPP service (dpp-validator)"),
                       ("operator", "Economic operator (self-declared)")]:
        items = [c for c in criteria if c["target"] == key]
        if items:
            out.append(row(label, items))
    out.append(row("**All criteria**", criteria))
    return out


def render(criteria):
    groups = grouped(criteria)
    out = [
        "<!-- Generated by scripts/render_criteria_md.py from criteria/*/*.yaml. "
        "Do not edit; change the YAML files and run the script. -->",
        "",
        "# DPP criteria catalogue",
        "",
        "Readable overview of all criteria in this folder. Each criterion is defined in one "
        "YAML file; this page is generated from those files, so the YAML file is the "
        "reference if the two ever differ. The file format is described in "
        "[CRITERIA-FORMAT.md](../CRITERIA-FORMAT.md).",
        "",
        "Statements paraphrase their sources; they are not quotations of the standards. "
        "Only `active` criteria count in published results; `proposed` criteria are under "
        "review. Results state how many automated checks passed on a given day. They are "
        "not a certification and do not establish a presumption of conformity.",
        "",
        "## Overview",
        "",
    ]
    out += counts_table(criteria)
    out += [
        "",
        "How to read the entries:",
        "",
        "- **Level**: MUST, SHOULD or MAY as in RFC 2119.",
        "- **Checked on**: *published passport* means the passport fetched via its product "
        "identifier (checked by [dpplint](https://github.com/OwnYourData/dpplint)); "
        "*DPP service* means the API of a listed service (checked daily by "
        "[dpp-validator](https://github.com/OwnYourData/dpp-validator)); *economic operator* "
        "means an obligation the operator declares.",
        "- **Method**: *automated* checks run from the public internet with test data only; "
        "*with test credentials* also needs a token from the operator; *self-declared* "
        "means the operator states it and links evidence.",
        "- **Results**: passed, failed, warning (passed with a remark) or skipped (condition "
        "not met or data not available). Only passed and failed count in \"N of M\".",
        "- **Placeholders** in requests: `{base}` API base of the service, `{dppId}` and "
        "`{productId}` its test passport ID and product identifier, `{elementIdPath}` a "
        "JSONPath into the test passport, `{randomId}` an ID no service has issued, `{now}` "
        "the run time in UTC.",
        "",
        "## Contents",
        "",
    ]
    for name, items in groups:
        out += [f"**{name}**", "",
                "| ID | Title | Level | Checked on | Status |",
                "|---|---|---|---|---|"]
        for c in items:
            out.append(f"| [{c['id']}](#{slug(heading(c))}) | {text(c['title'])} | "
                       f"{c['level']} | {TARGET.get(c['target'], c['target'])} | {c['status']} |")
        out.append("")
    for name, items in groups:
        out += [f"## {name}", ""]
        for c in items:
            out += criterion_section(c)
    return "\n".join(out).rstrip() + "\n"


def main():
    check = "--check" in sys.argv[1:]
    page = render(load())
    if check:
        try:
            with open(OUT, encoding="utf-8") as f:
                current = f.read()
        except FileNotFoundError:
            current = None
        if current != page:
            print("criteria/README.md is out of date: run python3 scripts/render_criteria_md.py "
                  "and commit the result.", file=sys.stderr)
            sys.exit(1)
        print("criteria/README.md is up to date.")
        return
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote criteria/README.md ({len(page.splitlines())} lines).")


if __name__ == "__main__":
    main()
