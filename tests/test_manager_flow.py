from __future__ import annotations

from pathlib import Path

import pytest

from skills import SkillsManager


def test_manager_handles_project_skill_lifecycle(tmp_path: Path, make_skill) -> None:
    source = tmp_path / "source"
    make_skill(source, "Python Style", "Prefer pathlib.")
    manager = SkillsManager(tmp_path)

    added = manager.add(str(source), skills=["python-style"], mode="copy")
    used = manager.use("python-style")
    installed = manager.installed()
    removed = manager.remove(["python-style"])

    assert [result.lock_entry.name for result in added] == ["python-style"]
    assert "Prefer pathlib." in used.prompt
    assert [entry.name for entry in installed] == ["python-style"]
    assert [result.name for result in removed] == ["python-style"]
    assert manager.installed() == []


def test_project_managers_keep_state_separate(tmp_path: Path, make_skill) -> None:
    source_a = tmp_path / "source-a"
    source_b = tmp_path / "source-b"
    make_skill(source_a, "shared-skill", "Project A.")
    make_skill(source_b, "shared-skill", "Project B.")
    project_a = tmp_path / "project-a"
    project_b = tmp_path / "project-b"
    project_a.mkdir()
    project_b.mkdir()

    manager_a = SkillsManager(project_a)
    manager_b = SkillsManager(project_b)
    manager_a.add(str(source_a), mode="copy")
    manager_b.add(str(source_b), mode="copy")

    assert "Project A." in manager_a.use("shared-skill").prompt
    assert "Project B." in manager_b.use("shared-skill").prompt
    assert manager_a.lock_path() == project_a / ".skills" / "skills.lock"
    assert manager_b.lock_path() == project_b / ".skills" / "skills.lock"


def test_manager_rejects_duplicate_normalized_skill_names(tmp_path: Path, make_skill) -> None:
    source = tmp_path / "source"
    make_skill(source, "Python Style")
    make_skill(source, "python-style")
    manager = SkillsManager(tmp_path)

    with pytest.raises(ValueError, match="duplicate skill names after normalization: python-style"):
        manager.add(str(source), mode="copy")


def test_manager_rejects_invalid_install_mode_before_writing_state(tmp_path: Path, make_skill) -> None:
    source = tmp_path / "source"
    make_skill(source, "agent-skill")
    manager = SkillsManager(tmp_path)

    with pytest.raises(ValueError, match="install mode must be symlink or copy"):
        manager.add(str(source), mode="hardlink")

    assert not (tmp_path / ".skills").exists()
    assert not (tmp_path / ".agents").exists()


def test_manager_installs_bundled_skills_source(tmp_path: Path) -> None:
    source = Path(__file__).parents[1] / "skills"
    manager = SkillsManager(tmp_path)

    added = manager.add(str(source), skills=["skills-manager"], mode="copy")
    prompt = manager.use("skills-manager").prompt

    assert [result.lock_entry.name for result in added] == ["skills-manager"]
    assert "SkillsManager" in prompt
    assert "cli -> SkillsManager -> features -> hooks/plugins" in prompt
