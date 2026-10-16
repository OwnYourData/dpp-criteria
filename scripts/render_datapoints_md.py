"""Renders the data points as one human-readable Markdown page: datapoints/README.md.

GitHub shows the page below the file list of the datapoints/ folder. It is
generated from datapoints/*/*.yaml and must not be edited by hand: change the
YAML file, run this script and commit both. CI runs it with --check.

Usage: python3 scripts/render_datapoints_md.py [--check]
Needs: pip install pyyaml
"""

import glob
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "datapoints", "README.md")

REGIMES = [
    ("ESPR", "Ecodesign for Sustainable Products Regulation (EU) 2024/1781"),
    ("TOY", "Toy Safety Regulation (EU) 2025/2509"),
    ("CPR", "Construction Products Regulation (EU) 2024/3110"),
    ("EUDR", "Deforestation Regulation (EU) 2023/1115"),
    ("BATT", "Batteries Regulation (EU) 2023/1542"),
]

REGIME_NOTES = {
    "BATT": [
        "Battery passports are required from 18 February 2027 for LMT batteries, industrial "
        "batteries with a capacity greater than 2 kWh and electric vehicle batteries "
        "(Art. 77(1)). The data points follow the numbering, the battery categories and the "
        "applicability of the European Commission's [Guidance Document: Digital Batteries "
        "Passport – data points by category, version 2.0 of 15 August 2026]"
        "(https://single-market-economy.ec.europa.eu/document/download/"
        "cd1e5e6c-4a4a-4b99-995a-49eb6916187e_en) (© European Union, 2026, CC BY 4.0); names and "
        "descriptions are paraphrased and the access and granularity entries are added from the "
        "Regulation. The guidance is not legally binding.",
    ],
}

BATTERY_CATEGORIES = [
    ("ev", "Electric vehicle batteries"),
    ("lmt", "LMT batteries"),
    ("industrial", "Industrial batteries > 2 kWh"),
]

STATUS = {
    "mandatory": "mandatory",
    "optional": "optional",
    "if-applicable": "if applicable",
    "not-to-be-filled": "not to be filled",
}

REASON = {
    "repetition": "repetition",
    "pending-implementing-act": "implementing act pending",
    "pending-delegated-act": "delegated act pending",
    "applies-later": "applies later",
    "on-hold": "on hold",
    "not-for-category": "not for this category",
}

TIERS = [
    ("fixed", "Fixed by ESPR for every passport"),
    ("minimum", "Fixed minimum content, may be narrowed by the delegated act"),
    ("conditional", "Conditional, triggered directly by ESPR or the registry regulation"),
    ("delegated-act", "Selected by the delegated act (ESPR Annex III)"),
    ("annex-i", "Product parameters selectable by the delegated act (ESPR Annex I)"),
    ("voluntary", "Voluntary, within the delegated act"),
    ("regime", "Required by the product-specific regulation"),
    ("sectoral", "Required by sectoral law outside the DPP rules"),
]

ACCESS = {
    "public": "public",
    "restricted": "restricted to named actors",
    "delegated-act": "set by the delegated act",
    "unspecified": "not specified",
}

KIND = {
    "regulation": "regulation",
    "harmonised-standard": "harmonised standard",
    "draft-standard": "draft standard",
    "standard": "standard",
    "guidance": "guidance",
    "derived": "derived",
}


def text(s):
    """Prose from a YAML field, with Markdown syntax characters escaped."""
    s = " ".join(str(s).split())
    s = s.replace("\\", "\\\\")
    for ch in "*_`[]<>|":
        s = s.replace(ch, "\\" + ch)
    return s


def load():
    items = []
    for path in sorted(glob.glob(os.path.join(ROOT, "datapoints", "*", "*.yaml"))):
        with open(path, encoding="utf-8") as f:
            d = yaml.safe_load(f)
        d["_file"] = os.path.relpath(path, os.path.join(ROOT, "datapoints")).replace(os.sep, "/")
        items.append(d)
    return items


def basis_line(b):
    src = text(b["source"])
    if b.get("url"):
        src = f"[{src}]({b['url']})"
    clause = f", {text(b['clause'])}" if b.get("clause") else ""
    return f"- {src}{clause} ({KIND.get(b['kind'], b['kind'])})"


def applicability_cell(a):
    parts = [STATUS[a["status"]]]
    if a.get("reason"):
        parts.append(REASON[a["reason"]])
    if a.get("same_as"):
        parts.append("see " + ", ".join(f"[{i}](#{i.lower()})" for i in a["same_as"]))
    if a.get("applies_from"):
        parts.append(f"from {a['applies_from']}")
    cell = " – ".join(parts[:2]) + ("; " + "; ".join(parts[2:]) if len(parts) > 2 else "")
    if a.get("note"):
        cell += ". " + text(a["note"])
    return cell


def section(d):
    out = [f"#### {d['id']}", "", f"**{text(d['name'])}**", ""]
    facts = [f"access: {ACCESS[d['access']]}", f"version {d['version']}"]
    if d.get("en18223_attribute"):
        facts.insert(0, f"EN 18223 attribute: `{d['en18223_attribute']}`")
    out += [" · ".join(facts), "", text(d["description"]), ""]
    rows = []
    if d.get("term"):
        rows.append(("Term in the legal act", text(d["term"])))
    if d.get("granularity"):
        rows.append(("Refers to", text(d["granularity"])))
    if d.get("provided_by"):
        rows.append(("Provided by", text(d["provided_by"])))
    if rows:
        out += ["| | |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows] + [""]
    if d.get("access_notes"):
        out += ["**Access** " + text(d["access_notes"]), ""]
    if d.get("battery_applicability"):
        ba = d["battery_applicability"]
        out += ["| Battery category | Applicability |", "|---|---|"]
        out += [f"| {label} | {applicability_cell(ba[key])} |" for key, label in BATTERY_CATEGORIES]
        out += [""]
    out += ["**Basis**", ""] + [basis_line(b) for b in d["basis"]] + [""]
    if d.get("notes"):
        out += ["**Notes** " + text(d["notes"]), ""]
    out += [f"Source: [{d['_file']}]({d['_file']})", ""]
    return out


def render(items):
    out = [
        "<!-- Generated by scripts/render_datapoints_md.py from datapoints/*/*.yaml. "
        "Do not edit; change the YAML files and run the script. -->",
        "",
        "# DPP data points",
        "",
        "Data points that EU legal acts require, allow or expect in a digital product "
        "passport, with their legal basis and what the act says about access. Each data "
        "point is defined in one YAML file; this page is generated from those files, so "
        "the YAML file is the reference if the two ever differ. The file format is "
        "described in [DATAPOINT-FORMAT.md](../DATAPOINT-FORMAT.md).",
        "",
        "Data points are reference material for criteria. They are not checked themselves "
        "and are not legal advice: which data points apply to a product follows from the "
        "delegated or product-specific act for its product group.",
        "",
        "## Overview",
        "",
    ]
    regimes = [(r, name) for r, name in REGIMES if any(d["regime"] == r for d in items)]
    accesses = [a for a in ACCESS if any(d["access"] == a for d in items)]
    out.append("| | " + " | ".join(ACCESS[a] for a in accesses) + " | total |")
    out.append("|---|" + "---:|" * (len(accesses) + 1))
    for r, name in regimes:
        sel = [d for d in items if d["regime"] == r]
        cells = [str(sum(1 for d in sel if d["access"] == a)) for a in accesses]
        out.append(f"| {name} | " + " | ".join(cells) + f" | {len(sel)} |")
    cells = [str(sum(1 for d in items if d["access"] == a)) for a in accesses]
    out.append("| **All data points** | " + " | ".join(cells) + f" | {len(items)} |")
    out += ["", "## Contents", ""]
    for r, name in regimes:
        out += [f"**{name}**", "", "| ID | Name | Access |", "|---|---|---|"]
        for d in sorted((d for d in items if d["regime"] == r), key=lambda d: d["id"]):
            out.append(f"| [{d['id']}](#{d['id'].lower()}) | {text(d['name'])} | {ACCESS[d['access']]} |")
        out.append("")
    for r, name in regimes:
        out += [f"## {name}", ""]
        for para in REGIME_NOTES.get(r, []):
            out += [para, ""]
        for tier, label in TIERS:
            sel = sorted((d for d in items if d["regime"] == r and d["tier"] == tier),
                         key=lambda d: d["id"])
            if not sel:
                continue
            out += [f"### {label}", ""]
            for d in sel:
                out += section(d)
    return "\n".join(out).rstrip() + "\n"


def main():
    page = render(load())
    if "--check" in sys.argv[1:]:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != page:
            print("datapoints/README.md is out of date: run python3 scripts/render_datapoints_md.py")
            sys.exit(1)
        print("datapoints/README.md is up to date")
        return
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
