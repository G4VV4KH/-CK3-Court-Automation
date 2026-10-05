"""Render README from the sole canonical publication description."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
(root / "README.md").write_bytes((root / "publishing/description.en.md").read_bytes())
