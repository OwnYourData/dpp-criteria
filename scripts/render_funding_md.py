"""Writes the funding notice of PACE-DPP into the "Funding" section of README.md.

The wording is kept once, in config/funding.yml. README.md holds a copy
between the markers <!-- funding:begin --> and <!-- funding:end -->; this
script replaces that copy. CI runs it with --check, which fails while the copy
differs from config/funding.yml or the section does not come before the
licence.

Usage: python3 scripts/render_funding_md.py [--check]
Needs: pip install pyyaml
"""

import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "config", "funding.yml")
README = os.path.join(ROOT, "README.md")
BEGIN_MARK = "<!-- funding:begin -->"
END_MARK = "<!-- funding:end -->"
REGION = re.compile(re.escape(BEGIN_MARK) + r".*?" + re.escape(END_MARK), re.S)


def markdown():
    """The notice for the README: Markdown, with the full title of the project."""
    with open(SOURCE, encoding="utf-8") as f:
        s = yaml.safe_load(f)
    return (
        s["text"]
        .replace("%{component}", s["component"])
        .replace("%{title}", " – " + s["title"])
    )


def main():
    check = "--check" in sys.argv[1:]
    with open(README, encoding="utf-8") as f:
        content = f.read()
    if not REGION.search(content):
        sys.exit("README.md: no funding markers")
    wanted = REGION.sub(lambda _: BEGIN_MARK + "\n" + markdown() + "\n" + END_MARK, content, count=1)
    order_ok = 0 <= content.find("## Funding") < content.find("## License")
    if check:
        if wanted != content:
            sys.exit("README.md: the funding notice differs from config/funding.yml; "
                     "run python3 scripts/render_funding_md.py")
        if not order_ok:
            sys.exit("README.md: the section Funding must come before the section License")
        print("README.md: funding notice matches config/funding.yml")
        return
    with open(README, "w", encoding="utf-8") as f:
        f.write(wanted)
    print("written: README.md")


if __name__ == "__main__":
    main()
