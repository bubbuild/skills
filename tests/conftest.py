from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def make_skill():
    return _make_skill


def _make_skill(root: Path, name: str, body: str = "Use this skill.") -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {name}
description: Example.
---

{body}
""",
        encoding="utf-8",
    )
    return skill_dir
