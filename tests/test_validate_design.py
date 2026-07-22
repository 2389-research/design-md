# ABOUTME: Tests for validate_design.py, which checks DESIGN.md files against
# ABOUTME: Google Labs spec basics: YAML validity, name, token refs, headings.
from pathlib import Path

import validate_design

VALID = """---
name: Acme
colors:
  primary: "#4f46e5"
  on-primary: "#ffffff"
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
---

# Acme Design

## Overview

Clean and dense.

## Colors

Primary is indigo.
"""


def check(text):
    return validate_design.validate_text(text)


def test_valid_file_has_no_issues():
    assert check(VALID) == []


def test_missing_name_is_an_issue():
    text = VALID.replace("name: Acme\n", "")
    assert any("name" in issue for issue in check(text))


def test_invalid_yaml_is_an_issue():
    text = VALID.replace("colors:", "colors: [unclosed")
    assert any("YAML" in issue for issue in check(text))


def test_unresolved_token_ref_is_an_issue():
    text = VALID.replace("{colors.primary}", "{colors.missing}")
    issues = check(text)
    assert any("colors.missing" in issue for issue in issues)


def test_duplicate_section_headings_rejected():
    text = VALID + "\n## Colors\n\nAgain.\n"
    assert any("duplicate" in issue.lower() for issue in check(text))


def test_no_front_matter_is_allowed():
    assert check("# Just prose\n\n## Overview\n\nWords.\n") == []


def test_dashes_line_inside_front_matter_does_not_terminate_it():
    text = VALID.replace(
        "name: Acme\n",
        "title: Acme Design System\n----: not a delimiter\nname: Acme\n",
    )
    assert check(text) == []


def test_crlf_front_matter_is_still_validated():
    text = VALID.replace("name: Acme\n", "").replace("\n", "\r\n")
    assert any("name" in issue for issue in check(text))


def test_non_dict_front_matter_is_an_issue():
    text = "---\njust a string\n---\n\n# T\n"
    assert any("mapping" in issue for issue in check(text))


def test_cli_exit_codes(tmp_path):
    good = tmp_path / "DESIGN.md"
    good.write_text(VALID)
    assert validate_design.main([str(good)]) == 0
    bad = tmp_path / "BAD.md"
    bad.write_text(VALID.replace("name: Acme\n", ""))
    assert validate_design.main([str(bad)]) == 1
