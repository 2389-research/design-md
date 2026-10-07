# ABOUTME: Pytest configuration: puts hook and validator script directories on
# ABOUTME: sys.path so tests can import them as modules.
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "hooks" / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))
