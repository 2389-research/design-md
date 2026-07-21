#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pyyaml"]
# ///
# ABOUTME: Validates a DESIGN.md file against Google Labs DESIGN.md spec basics:
# ABOUTME: YAML front matter, required name, token reference resolution, headings.
import re
import sys

import yaml

TOKEN_REF = re.compile(r"\{([a-zA-Z0-9_.\-]+)\}")


FRONT_MATTER_CLOSE = re.compile(r"\n---[ \t]*(?:\r?\n|$)")


def split_front_matter(text: str):
    if text.startswith("---\r\n") or text.startswith("---\n"):
        text = text.replace("\r\n", "\n")
    else:
        return None, text
    match = FRONT_MATTER_CLOSE.search(text, 3)
    if match is None:
        return None, text
    return text[4 : match.start()], text[match.end() :]


def resolve(ref: str, data: dict) -> bool:
    node = data
    for part in ref.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def iter_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from iter_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_strings(value)


def validate_text(text: str) -> list[str]:
    issues: list[str] = []
    raw_front, body = split_front_matter(text)
    front = None
    if raw_front is not None:
        try:
            front = yaml.safe_load(raw_front)
        except yaml.YAMLError as exc:
            issues.append(f"front matter is not valid YAML: {exc}")
        else:
            if not isinstance(front, dict):
                issues.append("front matter must be a YAML mapping")
        if isinstance(front, dict):
            if not front.get("name"):
                issues.append("front matter missing required 'name'")
            for value in iter_strings(front):
                for ref in TOKEN_REF.findall(value):
                    if not resolve(ref, front):
                        issues.append(f"unresolved token reference: {ref}")
    headings = re.findall(r"^## (.+)$", body, flags=re.MULTILINE)
    seen = set()
    for heading in headings:
        key = heading.strip().lower()
        if key in seen:
            issues.append(f"duplicate section heading: {heading.strip()}")
        seen.add(key)
    return issues


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: validate_design.py <path-to-DESIGN.md>", file=sys.stderr)
        return 2
    text = open(argv[0], encoding="utf-8").read()
    issues = validate_text(text)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
