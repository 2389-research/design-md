# design-md Plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the `design-md` Claude Code plugin: two skills (`design-md` create/revise, `using-design` enforcement), pre/post hooks, a spec-compliant DESIGN.md template, a validator, and scenario evals.

**Architecture:** Self-contained plugin repo (same shape as sibling `jam`/`intent` repos). Python 3 stdlib-only hook scripts wired via `hooks/hooks.json` (SessionStart/UserPromptSubmit pointer injection, Stop audit). Skills are SKILL.md markdown. A `uv`-scripted validator checks generated DESIGN.md files against the Google Labs spec basics.

**Tech Stack:** Python 3 (stdlib for hooks; PyYAML via uv PEP-723 header for validator), pytest via `uv run`, Claude Code plugin conventions (`.claude-plugin/plugin.json`, `skills/*/SKILL.md`, `hooks/hooks.json`).

**Design doc:** `docs/plans/2026-07-20-design-md-skill-design.md` — read it first; it is the source of truth for behavior.

**Test command (used throughout):**

```bash
uv run --with pytest --with pyyaml -- pytest tests/ -v
```

---

### Task 1: Plugin scaffolding

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `README.md` (stub — full version in Task 10)

**Step 1: Create `.claude-plugin/plugin.json`**

```json
{
  "name": "design-md",
  "version": "0.1.0",
  "description": "Create, revise, and enforce a DESIGN.md design system file (Google Labs spec-aligned). Extracts design taste from non-designers via react-don't-describe variant loops; hooks keep agents building against the design.",
  "author": {
    "name": "2389 Research"
  },
  "license": "MIT",
  "keywords": [
    "design",
    "design-system",
    "design-md",
    "design-tokens",
    "visual-identity",
    "hooks"
  ]
}
```

**Step 2: Create `LICENSE`** — standard MIT license text, copyright `2026 2389 Research`.

**Step 3: Create `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
```

**Step 4: Create `README.md` stub**

```markdown
# design-md

Claude Code plugin: create, revise, and enforce a DESIGN.md design system file.

Work in progress — see docs/plans/ for the design.
```

**Step 5: Commit**

```bash
git add .claude-plugin/plugin.json LICENSE .gitignore README.md
git commit -m "feat: scaffold design-md plugin (manifest, license, readme stub)"
```

---

### Task 2: DESIGN.md template

**Files:**
- Create: `templates/DESIGN.template.md`

**Step 1: Create the template.** Spec-compliant skeleton: YAML front matter with token maps, body sections in spec order, plus our extension sections (Terminal & CLI, Voice & Copy, Documents). HTML comments guide the skill filling it in; the skill deletes irrelevant sections and all guidance comments.

````markdown
---
version: alpha
name: PROJECT_NAME
description: One-line description of this design system.
colors:
  primary: "#4f46e5"
  on-primary: "#ffffff"
  surface: "#ffffff"
  on-surface: "#1f2937"
  neutral: "#6b7280"
  error: "#dc2626"
typography:
  headline-lg:
    fontFamily: "Inter, sans-serif"
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.2
  body-md:
    fontFamily: "Inter, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  label-sm:
    fontFamily: "Inter, sans-serif"
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.3
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
rounded:
  sm: 4px
  md: 8px
  full: 9999px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm} {spacing.md}"
---

# PROJECT_NAME Design

## Overview

<!-- Brand personality, audience, emotional intent. 3-6 sentences.
     Include the WHY behind the overall direction, citing user reactions
     from the creation session, e.g.:
     "Dense, information-first layout: user rejected two airy variants as
     'too empty' and pointed at variant 3's tables as 'exactly right'." -->

## Colors

<!-- Semantic roles and usage rules for each palette entry. One line of
     rationale per choice. -->

## Typography

<!-- Font strategy and hierarchy. When to use each level. -->

## Layout

<!-- Grid model, spacing scale usage, density rules, containment. -->

## Elevation & Depth

<!-- Shadow/tonal strategy. DELETE if irrelevant (e.g., CLI-only project). -->

## Shapes

<!-- Corner radius philosophy. DELETE if irrelevant. -->

## Components

<!-- Styling guidance per component beyond the tokens: states, variants,
     when to use which. -->

## Terminal & CLI

<!-- EXTENSION SECTION (preserved by spec parsers). DELETE if project has
     no CLI/TUI surface. Cover: ANSI color usage (map to color tokens where
     possible), output density, progress/spinner conventions, error
     formatting, table-vs-prose bias, verbosity defaults. -->

## Voice & Copy

<!-- EXTENSION SECTION. Tone, error-message style, microcopy rules,
     naming conventions. Applies across every medium. -->

## Documents

<!-- EXTENSION SECTION. README/deck/one-pager aesthetics. DELETE if
     irrelevant. -->

## Do's and Don'ts

<!-- Practical guardrails. Include don'ts sourced from user rejections
     during creation ("Don't use gradients — user: 'looks like a crypto
     site'"). -->
````

**Step 2: Commit**

```bash
git add templates/DESIGN.template.md
git commit -m "feat: add spec-compliant DESIGN.md template with extension sections"
```

---

### Task 3: Pre-hook script (`design_context.py`) — TDD

**Files:**
- Create: `hooks/scripts/design_context.py`
- Create: `tests/conftest.py`
- Test: `tests/test_design_context.py`

**Step 1: Create `tests/conftest.py`**

```python
# ABOUTME: Pytest configuration: puts hook and validator script directories on
# ABOUTME: sys.path so tests can import them as modules.
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "hooks" / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))
```

**Step 2: Write the failing tests**

```python
# ABOUTME: Tests for design_context.py, the SessionStart/UserPromptSubmit hook
# ABOUTME: that injects a pointer when the project contains a DESIGN.md.
import json
import subprocess
import sys
from pathlib import Path

import design_context

SCRIPT = Path(__file__).parent.parent / "hooks" / "scripts" / "design_context.py"


def test_finds_design_md_in_cwd(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    assert design_context.find_design_md(tmp_path) == tmp_path / "DESIGN.md"


def test_finds_design_md_walking_up_to_git_root(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "DESIGN.md").write_text("# design")
    sub = tmp_path / "src" / "components"
    sub.mkdir(parents=True)
    assert design_context.find_design_md(sub) == tmp_path / "DESIGN.md"


def test_stops_at_git_root(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")  # outside the repo
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    assert design_context.find_design_md(repo) is None


def test_none_when_absent(tmp_path):
    (tmp_path / ".git").mkdir()
    assert design_context.find_design_md(tmp_path) is None


def run_hook(payload):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_emits_pointer_when_design_md_exists(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    result = run_hook({"cwd": str(tmp_path)})
    assert result.returncode == 0
    assert "DESIGN.md" in result.stdout
    assert "using-design" in result.stdout


def test_silent_when_no_design_md(tmp_path):
    (tmp_path / ".git").mkdir()
    result = run_hook({"cwd": str(tmp_path)})
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_silent_on_malformed_stdin(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], input="not json", capture_output=True, text=True
    )
    assert result.returncode == 0
```

**Step 3: Run tests to verify they fail**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_design_context.py -v`
Expected: FAIL / ERROR with `ModuleNotFoundError: No module named 'design_context'`

**Step 4: Write the implementation**

```python
#!/usr/bin/env python3
# ABOUTME: Pre-hook for SessionStart and UserPromptSubmit: if the project has a
# ABOUTME: DESIGN.md, inject a one-line pointer to invoke the using-design skill.
import json
import sys
from pathlib import Path

POINTER = (
    "This project has a design system file: {path}. Before any work that "
    "changes user-visible output (UI, styling, terminal output, user-facing "
    "copy), invoke the using-design skill and conform to DESIGN.md."
)


def find_design_md(start: Path) -> Path | None:
    current = Path(start).resolve()
    for candidate in [current, *current.parents]:
        design = candidate / "DESIGN.md"
        if design.is_file():
            return design
        if (candidate / ".git").exists():
            return None
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    cwd = Path(data.get("cwd") or Path.cwd())
    design = find_design_md(cwd)
    if design is None:
        return
    print(POINTER.format(path=design))


if __name__ == "__main__":
    main()
```

**Step 5: Run tests to verify they pass**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_design_context.py -v`
Expected: 7 PASS

**Step 6: Commit**

```bash
git add hooks/scripts/design_context.py tests/conftest.py tests/test_design_context.py
git commit -m "feat: add DESIGN.md pointer pre-hook with tests"
```

---

### Task 4: Post-hook script (`design_audit.py`) — TDD

**Files:**
- Create: `hooks/scripts/design_audit.py`
- Test: `tests/test_design_audit.py`

Behavior (from design doc): on Stop, if the project has DESIGN.md AND this turn used a file-writing tool, emit `{"decision": "block", "reason": <audit prompt>}` so the agent audits user-visible changes against DESIGN.md. Silent when `stop_hook_active` (loop guard), when no DESIGN.md, or when the turn wrote nothing.

Transcript format note: Claude Code transcripts are JSONL; each entry has a `type` (`user`/`assistant`) and a `message` whose `content` is a list of blocks (`{"type": "tool_use", "name": "Edit", ...}`, `{"type": "tool_result", ...}`, `{"type": "text", ...}`). A "real" user message (turn boundary) is a `user` entry whose content contains no `tool_result` blocks. Parse leniently — skip lines that fail `json.loads`.

**Step 1: Write the failing tests**

```python
# ABOUTME: Tests for design_audit.py, the Stop hook that requests a design
# ABOUTME: conformance audit after turns that modified files.
import json
import subprocess
import sys
from pathlib import Path

import design_audit

SCRIPT = Path(__file__).parent.parent / "hooks" / "scripts" / "design_audit.py"


def make_transcript(tmp_path, entries):
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in entries))
    return p


def user_msg(text):
    return {"type": "user", "message": {"content": [{"type": "text", "text": text}]}}


def tool_result_msg():
    return {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}}


def assistant_tool_use(name):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": {}}]}}


def test_detects_write_tool_in_last_turn(tmp_path):
    t = make_transcript(tmp_path, [
        user_msg("hi"),
        assistant_tool_use("Read"),
        user_msg("change the button"),
        assistant_tool_use("Edit"),
        tool_result_msg(),
    ])
    assert design_audit.turn_modified_files(t) is True


def test_ignores_writes_from_earlier_turns(tmp_path):
    t = make_transcript(tmp_path, [
        user_msg("build it"),
        assistant_tool_use("Write"),
        tool_result_msg(),
        user_msg("thanks, what does it do?"),
        assistant_tool_use("Read"),
    ])
    assert design_audit.turn_modified_files(t) is False


def test_tool_results_are_not_turn_boundaries(tmp_path):
    t = make_transcript(tmp_path, [
        user_msg("change the button"),
        assistant_tool_use("Edit"),
        tool_result_msg(),
        assistant_tool_use("Bash"),
    ])
    assert design_audit.turn_modified_files(t) is True


def test_false_for_missing_transcript(tmp_path):
    assert design_audit.turn_modified_files(tmp_path / "nope.jsonl") is False


def test_skips_malformed_lines(tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text("garbage\n" + json.dumps(user_msg("x")) + "\n" + json.dumps(assistant_tool_use("Edit")))
    assert design_audit.turn_modified_files(p) is True


def run_hook(payload):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_blocks_with_audit_prompt(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Edit")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": False})
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["decision"] == "block"
    assert "DESIGN.md" in out["reason"]


def test_silent_when_stop_hook_active(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Edit")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": True})
    assert result.stdout.strip() == ""


def test_silent_when_no_design_md(tmp_path):
    (tmp_path / ".git").mkdir()
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Edit")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": False})
    assert result.stdout.strip() == ""


def test_silent_when_turn_wrote_nothing(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Read")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": False})
    assert result.stdout.strip() == ""
```

**Step 2: Run tests to verify they fail**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_design_audit.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'design_audit'`

**Step 3: Write the implementation**

```python
#!/usr/bin/env python3
# ABOUTME: Stop hook: after a turn that modified files in a project with a
# ABOUTME: DESIGN.md, block once and request a conformance audit against it.
import json
import sys
from pathlib import Path

from design_context import find_design_md

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}

AUDIT_PROMPT = (
    "Design audit: this turn modified files and the project has a design "
    "system file ({path}). If any change affects user-visible output (UI, "
    "styling, terminal output, user-facing copy), review it against DESIGN.md "
    "like a code review: report conformance and divergences, then fix "
    "divergences or explicitly flag them with reasoning. If nothing "
    "user-visible changed, state that no design audit is needed and stop."
)


def _is_tool_result(entry: dict) -> bool:
    content = entry.get("message", {}).get("content")
    if isinstance(content, list):
        return any(
            isinstance(b, dict) and b.get("type") == "tool_result" for b in content
        )
    return False


def turn_modified_files(transcript_path: Path) -> bool:
    if not Path(transcript_path).is_file():
        return False
    entries = []
    for line in Path(transcript_path).read_text().splitlines():
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    last_user = -1
    for i, entry in enumerate(entries):
        if entry.get("type") == "user" and not _is_tool_result(entry):
            last_user = i
    for entry in entries[last_user + 1 :]:
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content") or []
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") in WRITE_TOOLS
            ):
                return True
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if data.get("stop_hook_active"):
        return
    cwd = Path(data.get("cwd") or Path.cwd())
    design = find_design_md(cwd)
    if design is None:
        return
    if not turn_modified_files(Path(data.get("transcript_path", ""))):
        return
    print(json.dumps({"decision": "block", "reason": AUDIT_PROMPT.format(path=design)}))


if __name__ == "__main__":
    main()
```

Note: `from design_context import find_design_md` works because Python puts the script's own directory on `sys.path` when run as `python3 hooks/scripts/design_audit.py`.

**Step 4: Run tests to verify they pass**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_design_audit.py -v`
Expected: 9 PASS

**Step 5: Commit**

```bash
git add hooks/scripts/design_audit.py tests/test_design_audit.py
git commit -m "feat: add post-turn design audit Stop hook with tests"
```

---

### Task 5: Hook wiring (`hooks/hooks.json`) — TDD

**Files:**
- Create: `hooks/hooks.json`
- Test: `tests/test_hooks_json.py`

**Step 1: Write the failing test**

```python
# ABOUTME: Tests that hooks.json is valid, wires the expected events, and
# ABOUTME: references hook scripts that actually exist in the repo.
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
HOOKS_JSON = ROOT / "hooks" / "hooks.json"


def test_hooks_json_is_valid_json():
    data = json.loads(HOOKS_JSON.read_text())
    assert set(data["hooks"].keys()) == {"SessionStart", "UserPromptSubmit", "Stop"}


def test_referenced_scripts_exist():
    data = json.loads(HOOKS_JSON.read_text())
    for event_hooks in data["hooks"].values():
        for matcher_group in event_hooks:
            for hook in matcher_group["hooks"]:
                match = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}/(\S+?)\"", hook["command"])
                assert match, f"no plugin-root path in: {hook['command']}"
                assert (ROOT / match.group(1)).is_file()
```

**Step 2: Run test to verify it fails**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_hooks_json.py -v`
Expected: FAIL with `FileNotFoundError` (hooks.json missing)

**Step 3: Create `hooks/hooks.json`**

```json
{
  "description": "design-md plugin hooks: DESIGN.md pointer injection (SessionStart, UserPromptSubmit) and post-turn design audit (Stop)",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/design_context.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/design_context.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/design_audit.py\"",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

**Step 4: Run test to verify it passes**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_hooks_json.py -v`
Expected: 2 PASS

**Step 5: Commit**

```bash
git add hooks/hooks.json tests/test_hooks_json.py
git commit -m "feat: wire pre/post design hooks in hooks.json"
```

---

### Task 6: DESIGN.md validator (`scripts/validate_design.py`) — TDD

**Files:**
- Create: `scripts/validate_design.py`
- Test: `tests/test_validate_design.py`

Checks (v1, from design doc): front matter parses as YAML; `name` present when front matter exists; `{token.ref}` references resolve within the front matter; duplicate `##` section headings rejected (per spec). Exit 0 + `OK` when clean; exit 1 with one issue per line otherwise.

**Step 1: Write the failing tests**

```python
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


def test_cli_exit_codes(tmp_path):
    good = tmp_path / "DESIGN.md"
    good.write_text(VALID)
    assert validate_design.main([str(good)]) == 0
    bad = tmp_path / "BAD.md"
    bad.write_text(VALID.replace("name: Acme\n", ""))
    assert validate_design.main([str(bad)]) == 1
```

**Step 2: Run tests to verify they fail**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_validate_design.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'validate_design'`

**Step 3: Write the implementation**

```python
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


def split_front_matter(text: str):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4 :]


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
```

**Step 4: Run tests to verify they pass**

Run: `uv run --with pytest --with pyyaml -- pytest tests/test_validate_design.py -v`
Expected: 7 PASS

**Step 5: Validate the template against the validator**

Run: `uv run --with pyyaml -- python3 scripts/validate_design.py templates/DESIGN.template.md`
Expected: `OK` (fix the template if not — this is a real check, template token refs must resolve)

**Step 6: Commit**

```bash
git add scripts/validate_design.py tests/test_validate_design.py
git commit -m "feat: add DESIGN.md spec validator with tests"
```

---

### Task 7: `design-md` skill (create + revise)

**Files:**
- Create: `skills/design-md/SKILL.md`

**Step 1: Write the skill.** Full content below — this is the deliverable, not pseudocode. It encodes the four-phase loop from the design doc.

````markdown
---
name: design-md
description: Use when creating or updating a DESIGN.md design system file, when the user wants to define how their project should look and feel, or when they express design desires they can't articulate ("make it look nice", "something clean", "I don't like it but can't say why"). Extracts design taste through concrete variants the user reacts to — no design vocabulary required. Triggers on "design.md", "DESIGN.md", "design system", "visual identity", "style this project", "make it look".
---

# design-md: Create or Revise a DESIGN.md

Produce a DESIGN.md — a machine-and-human-readable design system file
(Google Labs DESIGN.md spec) — by showing the user concrete rendered
variants and capturing their reactions. Never ask a non-designer to
describe design in words; show them things and let them point.

**Core rule: taste is extracted by reaction, not introspection.**

## Entry states

- **Create:** no DESIGN.md exists. Run all four phases.
- **Revise:** DESIGN.md exists and the user wants a change ("darker",
  "less cramped", "new brand color"). Seed = current DESIGN.md + the
  requested change; run Phases 2-4 scoped to what's changing.

## Phase 1 — Seed (cheap signal before generating anything)

Collect, in one short exchange each (skip any that are already answered):

1. **References:** "Name 2-3 sites, apps, or CLIs whose look you like —
   or hate." Translate names into concrete attributes yourself (Linear →
   dark, dense, keyboard-first; Stripe → airy, generous whitespace,
   restrained color).
2. **Micro-interview:** at most 4 multiple-choice questions. Every option
   MUST be anchored to a named familiar thing, never jargon:
   - "Dense like a Bloomberg terminal / airy like Apple.com / between,
     like Stripe?"
   - "Colorful like Figma / restrained like Notion / monochrome + one
     accent like Linear?"
   Never ask "what typography do you want?" or use terms like
   "elevation", "tonal", "grid system" in questions.
3. **Existing output:** if the project already renders anything (UI
   pages, CLI output, README), capture it and treat it as an implicit
   reference — extract its current palette/density/tone as one seed
   among others.

Do not skip to Phase 2 with zero signal; one reference or one answered
question is enough.

## Phase 2 — React (generate divergent variants)

Generate 3-4 genuinely divergent variants in the project's medium, in a
scratch directory (`/tmp/design-md-<project>/` or similar). Variants are
throwaway; only DESIGN.md is ever committed.

**Web/app UI:** one self-contained HTML file (`gallery.html`, no external
dependencies, system/web-safe font stacks or embedded @font-face) showing
the SAME realistic page content styled 3-4 ways, clearly labeled
Variant 1..4. Use content from the actual project when possible (its real
nav items, real data). Open it in the user's browser.

**CLI/TUI:** one script (bash or python) that prints the SAME output — a
table, a progress run, an error message — in 3-4 styles varying color
usage, density, ornamentation (rules/boxes vs bare), and tone. Run it so
the user sees real terminal rendering.

**Documents:** 3-4 renderings of the same one-pager/README section.

Variants must disagree with each other on real axes (density, color
temperature, ornament, formality). Four near-identical variants teach
nothing.

**Ask for reactions, not descriptions:** "Point at anything you like or
hate, per variant. Fragments are perfect: '2's colors, 1's density, hate
all the fonts' is a great answer."

## Phase 3 — Converge

Synthesize reactions into one merged variant; render it next to the
closest runner-up and ask again. Typical session: 1-2 rounds. The user
can stop at any time ("that one") — never force another round. If
reactions conflict ("liked 1's density" + "liked 3's whitespace"),
render the tension as two sub-variants rather than asking them to
resolve it verbally.

## Phase 4 — Write

1. Copy `templates/DESIGN.template.md` (in this plugin) to `DESIGN.md`
   at the project root.
2. Fill YAML front matter with tokens extracted from the winning
   variant: colors, typography levels, spacing scale, rounded scale,
   component tokens (use `{token.ref}` cross-references).
3. Fill prose sections. **Every choice gets a one-line why, and user
   reactions ARE the rationale:** "Dense layout: user rejected two airy
   variants as 'too empty'." Rejections go in Do's and Don'ts:
   "Don't use gradients — user: 'looks like a crypto site'."
4. Delete sections irrelevant to the project's media, and delete all
   template guidance comments.
5. Validate: run the plugin's `scripts/validate_design.py DESIGN.md`.
   Fix any issues before presenting.
6. Close with a delta summary (what the design says in 3 lines) plus the
   single weakest assumption, asked once. No confirmation checklists.

## Revision rules

- Never silently rewrite tokens. Render current vs proposed side by side
  (same gallery/script mechanism, 2 variants) before writing.
- Surface ripple effects: "changing colors.primary affects
  components.button-primary and the Colors prose."
- Preserve existing rationale lines unless the user's new reaction
  contradicts them — then update the rationale, citing the new reaction.
- Re-run the validator after every revision.

## Non-designer principles (apply throughout)

- Multiple choice over open-ended; named references over adjectives;
  reactions over descriptions.
- Fragments and negative reactions are first-class data. "I hate it" is
  a fine start — render the opposite and ask again.
- Never use design jargon in a question. Using it in DESIGN.md prose is
  fine — that file is for agents too.
- One question per message during seeding.
````

**Step 2: Sanity-check frontmatter** — YAML parses, `name` matches directory:

Run: `uv run --with pyyaml -- python3 -c "import yaml,pathlib; t=pathlib.Path('skills/design-md/SKILL.md').read_text(); print(yaml.safe_load(t.split('---')[1])['name'])"`
Expected: `design-md`

**Step 3: Commit**

```bash
git add skills/design-md/SKILL.md
git commit -m "feat: add design-md skill (create/revise via react-don't-describe loop)"
```

---

### Task 8: `using-design` skill (enforcement)

**Files:**
- Create: `skills/using-design/SKILL.md`

**Step 1: Write the skill.** Full content:

````markdown
---
name: using-design
description: Use before any work that changes user-visible output — UI, styling, components, pages, terminal/CLI output, or user-facing copy — in a project that contains a DESIGN.md. Loads the design system, builds with its tokens, and self-checks the result against it before presenting. Also invoked by the design-md plugin hooks.
---

# using-design: Build Against DESIGN.md

When work touches anything a user will see, DESIGN.md is the contract.
Read it, build with it, and check your output against it BEFORE the user
sees the result.

## Step 1 — Load

Read `DESIGN.md` at the project root before writing any code.

- **Tokens are law:** front-matter values (colors, typography, spacing,
  rounded, components) are exact. Never eyeball-approximate them.
- **Prose is judgment guidance:** Overview, section rationale, and
  Do's and Don'ts tell you how to apply tokens to situations the tokens
  don't literally cover.

If the work clearly touches nothing user-visible (pure backend logic,
build config, tests), say so in one line and proceed without the rest of
this workflow.

## Step 2 — Build with tokens by reference

- Web: consume tokens as CSS custom properties / theme constants named
  after the front-matter tokens (`--color-primary`, `--spacing-md`). If
  the project has no token layer yet, create one from the front matter
  rather than scattering literals.
- Never re-derive values ("that's roughly #4f46e5") — copy the token.
- CLI/TUI: follow the Terminal & CLI section for color usage, density,
  progress conventions, and error formatting.
- Copy/microcopy: follow Voice & Copy for tone and error style.
- New component? Check the Components section and existing component
  tokens for the nearest precedent before inventing.

## Step 3 — Self-check before presenting

After building, diff your output against DESIGN.md and fix violations
BEFORE showing the user:

- [ ] Every color used is a token (or derived per an explicit rule in
      the prose)
- [ ] Type sizes/weights map to defined typography levels
- [ ] Spacing values come from the spacing scale
- [ ] Corner radii come from the rounded scale
- [ ] Nothing violates Do's and Don'ts
- [ ] User-facing text matches Voice & Copy
- [ ] Terminal output matches Terminal & CLI (if applicable)

Fix what you find. Then report in one or two lines: "Design check:
conforms" or "Design check: 2 divergences fixed (off-scale padding,
non-token gray)."

## Step 4 — Conform or surface (never improvise silently)

If DESIGN.md genuinely cannot express what's needed — a new component
with no precedent, a missing semantic color, a medium it doesn't cover:

1. Build it as close to the existing system as possible.
2. Surface the gap explicitly: "DESIGN.md has no 'warning' color; I used
   colors.error at 60% as a stopgap. Proposed addition: ..."
3. Offer to update DESIGN.md via the design-md skill (revision flow).

Divergence is allowed only when explicit. Silent divergence is the
failure mode this skill exists to prevent.

## No DESIGN.md?

If substantial user-visible work is starting and the project has no
DESIGN.md, offer ONCE: "This project has no DESIGN.md — want to create
one first so this and future work stays consistent? (design-md skill,
~10 minutes)." If declined, proceed and do not ask again this session.
````

**Step 2: Sanity-check frontmatter**

Run: `uv run --with pyyaml -- python3 -c "import yaml,pathlib; t=pathlib.Path('skills/using-design/SKILL.md').read_text(); print(yaml.safe_load(t.split('---')[1])['name'])"`
Expected: `using-design`

**Step 3: Commit**

```bash
git add skills/using-design/SKILL.md
git commit -m "feat: add using-design enforcement skill"
```

---

### Task 9: Scenario evals

**Files:**
- Create: `evals/README.md`
- Create: `evals/scenarios/01-non-designer-creation.md`
- Create: `evals/scenarios/02-enforcement-token-violation.md`
- Create: `evals/scenarios/03-revision-ripple.md`

These are manual/agent-run scenario scripts (jam/intent convention), not automated pytest.

**Step 1: Create `evals/README.md`**

```markdown
# design-md Evals

Scenario-based evaluations. Each scenario file defines: setup, the prompt
to give a fresh Claude Code session with this plugin installed, and pass
criteria. Run them manually or via a driver agent; record results in
`evals/results/<scenario>/<date>.md`.

| # | Scenario | Exercises |
|---|----------|-----------|
| 01 | Non-designer creation | design-md skill, Phases 1-4 |
| 02 | Enforcement + token violation | hooks, using-design self-check |
| 03 | Revision ripple | design-md revision guard |
```

**Step 2: Create `evals/scenarios/01-non-designer-creation.md`**

```markdown
# 01 — Non-designer creation

## Setup
Empty project directory with a minimal web app (one HTML page, no styling
direction). Plugin installed.

## Prompt
"I want this to look nice and clean but I'm honestly bad at design.
Can you set up a design for this project?"

## Pass criteria
- [ ] design-md skill invoked (not ad-hoc styling)
- [ ] Seeding questions are ≤4, multiple-choice, anchored to named
      familiar products; zero design jargon in questions
- [ ] 3-4 genuinely divergent variants rendered as a self-contained HTML
      gallery and opened in the browser
- [ ] User reactions requested as point-at-things, fragments welcomed
- [ ] DESIGN.md written at project root, passes validate_design.py
- [ ] Rationale lines cite the user's actual reactions
- [ ] Variants left in scratch dir, not committed

## Fail modes to watch
- Asks "what fonts/colors do you want?" (introspection, not reaction)
- Variants differ only trivially (same layout, four accent colors)
- DESIGN.md written without any variant round
```

**Step 3: Create `evals/scenarios/02-enforcement-token-violation.md`**

```markdown
# 02 — Enforcement + token violation

## Setup
Project with a committed DESIGN.md (use templates/DESIGN.template.md
filled with concrete values) and a small web page that uses its tokens.

## Prompt
"Add a signup banner to the top of the page with a nice green call-to-action
button."

(Note: DESIGN.md defines no green; primary is indigo.)

## Pass criteria
- [ ] Pre-hook pointer appears in context; using-design skill invoked
      before edits
- [ ] Agent either uses colors.primary for the CTA or surfaces the gap
      explicitly ("no green token — options: ...") — it does NOT silently
      hardcode a green hex
- [ ] Self-check report appears before presenting ("Design check: ...")
- [ ] Stop-hook audit runs after the turn and its conclusion matches
      reality

## Fail modes to watch
- Banner built with literal colors despite DESIGN.md
- Audit reports "conforms" when a divergence exists
- Audit loops (stop_hook_active guard failing)
```

**Step 4: Create `evals/scenarios/03-revision-ripple.md`**

```markdown
# 03 — Revision ripple

## Setup
Project with DESIGN.md whose components reference {colors.primary}.

## Prompt
"Actually I think the primary color should be a warm orange instead."

## Pass criteria
- [ ] design-md skill revision flow: current vs proposed rendered side
      by side BEFORE any file change
- [ ] Ripple effects surfaced (components referencing colors.primary,
      Colors prose, contrast with on-primary)
- [ ] Existing rationale updated, not deleted; new reaction recorded
- [ ] validate_design.py re-run after the write

## Fail modes to watch
- Token silently rewritten with no rendering
- on-primary left unreadable against the new orange with no mention
```

**Step 5: Commit**

```bash
git add evals/
git commit -m "feat: add scenario evals for creation, enforcement, and revision"
```

---

### Task 10: Full README + final verification

**Files:**
- Modify: `README.md` (replace stub)

**Step 1: Write the full README.** Cover: what DESIGN.md is (link Google spec repo), what the plugin does (create/revise via reactions, enforce via skill + hooks), the two skills, how the hooks behave (and that they're inert without a DESIGN.md), install instructions (marketplace + manual), the extension sections, repo layout, running tests, license. Keep it factual; no marketing voice. Note explicitly: works for web UI, CLI/TUI, documents, and voice/copy — not web-only.

**Step 2: Run the entire test suite**

Run: `uv run --with pytest --with pyyaml -- pytest tests/ -v`
Expected: all tests pass (7 + 9 + 2 + 7 = 25)

**Step 3: Validate the template one more time**

Run: `uv run --with pyyaml -- python3 scripts/validate_design.py templates/DESIGN.template.md`
Expected: `OK`

**Step 4: REQUIRED SUB-SKILL — superpowers:verification-before-completion** before claiming done.

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: full README for design-md plugin"
```

---

## Out of scope (do not build)

- Standalone extraction skill, monorepo multi-DESIGN.md, Figma/Stitch
  integration, Google token CLI tooling (see design doc NOT-doing list)
- Marketplace listing edits (2389 research marketplace entry happens in
  that repo, separately, after this plugin works)

## Post-plan follow-ups (not tasks here)

- Run eval scenario 01 end-to-end in a throwaway project; iterate on the
  design-md SKILL.md wording based on what the agent actually does.
- Add the plugin to the 2389 research marketplace and (optionally) publish
  the standalone repo.
