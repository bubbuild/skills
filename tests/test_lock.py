from __future__ import annotations

from pathlib import Path

import pytest

from skills.lock import InvalidLockError, SkillLock


def test_lock_read_rejects_missing_metadata(tmp_path: Path) -> None:
    lock_path = tmp_path / "skills.lock"
    lock_path.write_text('[skill.example]\nsource = "source"\n', encoding="utf-8")

    with pytest.raises(InvalidLockError, match=r"missing \[metadata\] table"):
        SkillLock.read(lock_path)


def test_lock_read_rejects_non_table_skills(tmp_path: Path) -> None:
    lock_path = tmp_path / "skills.lock"
    lock_path.write_text(
        """
skill = ["example"]

[metadata]
lock_version = "1.0"
""",
        encoding="utf-8",
    )

    with pytest.raises(InvalidLockError, match=r"\[skill\] must be a table"):
        SkillLock.read(lock_path)
