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
