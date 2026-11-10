"""Verify three README badge blocks against real pytest JUnit XML.

CI runs this after pytest, which prevents a stale green test-count badge.
No API calls, secrets, or repository mutations are performed.
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READMES = ("README.md", "README.pt-BR.md", "README.es.md")
START = "<!-- BADGES:START -->"
END = "<!-- BADGES:END -->"
EXPECTED_BADGES = 21


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--junitxml", required=True, type=Path)
    args = parser.parse_args()

    xml = ET.parse(args.junitxml)
    suite = xml.getroot().find(".//testsuite")
    if suite is None:
        raise SystemExit("JUnit XML contains no testsuite")
    total = int(suite.attrib["tests"])
    failed = int(suite.attrib.get("failures", "0"))
    errors = int(suite.attrib.get("errors", "0"))
    skipped = int(suite.attrib.get("skipped", "0"))
    passed = total - failed - errors - skipped
    if passed <= 0 or failed or errors:
        raise SystemExit("Cannot publish a passing badge with failed tests")

    baseline = None
    for name in READMES:
        text = (ROOT / name).read_text(encoding="utf-8")
        if text.count(START) != 1 or text.count(END) != 1:
            raise SystemExit(f"{name}: missing or duplicate badge markers")
        section = text.split(START, 1)[1].split(END, 1)[0].strip()
        count = len(re.findall(r"!\\[[^]]+\\]\\(", section))
        if count != EXPECTED_BADGES:
            raise SystemExit(f"{name}: expected {EXPECTED_BADGES} badges, got {count}")
        if f"pytest-{passed}%20passing-" not in section:
            raise SystemExit(f"{name}: pytest badge differs from {passed} real passes")
        if baseline is None:
            baseline = section
        elif section != baseline:
            raise SystemExit(f"{name}: badges differ across languages")
        for other in READMES:
            if f"]({other})" not in text:
                raise SystemExit(f"{name}: missing language link {other}")
        links = re.findall(r"\\]\\(([^)]+)\\)", text)
        for link in links:
            if link.startswith(("https://", "http://", "#", "mailto:")):
                continue
            local = link.split("#", 1)[0]
            if local and not (ROOT / local).exists():
                raise SystemExit(f"{name}: missing local link target {local}")

    print(
        f"README audit passed: {len(READMES)} locales, {EXPECTED_BADGES} badges, {passed} real passing tests"
    )


if __name__ == "__main__":
    main()
