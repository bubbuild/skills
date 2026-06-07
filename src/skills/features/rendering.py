from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skills.features.discovery import Skill, discover_skills
from skills.features.installing import MissingInstalledSkillsError, MissingSkillsError, project_lock_path
from skills.features.names import index_skills_by_normalized_name, normalize_skill_name
from skills.lock import SkillLock
from skills.project import Project


@dataclass(frozen=True)
class UseOptions:
    source_or_name: str
    skill: str | None = None
    global_install: bool = False
    refresh: bool = False


@dataclass(frozen=True)
class UseResult:
    skill: Skill
    prompt: str
    source_path: Path


def render_skill(project: Project, options: UseOptions) -> UseResult:
    installed = _render_installed(project, options)
    if installed is not None:
        return installed
    return _render_source(project, options)


def _render_installed(project: Project, options: UseOptions) -> UseResult | None:
    if options.skill is not None:
        return None

    name = normalize_skill_name(options.source_or_name)
    lock = SkillLock.read(project_lock_path(project, global_install=options.global_install))
    entry = lock.entries.get(name)
    if entry is None:
        return None
    skill = _read_single_skill(Path(entry.skill_path), name)
    return _render_result(project, skill)


def _render_source(project: Project, options: UseOptions) -> UseResult:
    hooks = project.require_hooks()
    parsed = hooks.parse_source(options.source_or_name)
    fetched = hooks.fetch_source(parsed, project, refresh=options.refresh)
    skills = discover_skills(fetched.root)
    selected = _select_one(skills, options.skill)
    return _render_result(project, selected)


def _render_result(project: Project, skill: Skill) -> UseResult:
    prompt = _read_prompt(skill.path)
    rendered = project.require_hooks().render_prompt(skill, prompt, project)
    return UseResult(skill=skill, prompt=rendered, source_path=skill.path)


def _select_one(skills: list[Skill], selected: str | None) -> Skill:
    if selected is None:
        if len(skills) == 1:
            return skills[0]
        raise AmbiguousSkillSelectionError([skill.name for skill in skills])

    safe_name = normalize_skill_name(selected)
    by_name = index_skills_by_normalized_name(skills)
    try:
        return by_name[safe_name]
    except KeyError as exc:
        raise MissingSkillsError([safe_name]) from exc


def _read_single_skill(path: Path, name: str) -> Skill:
    skills = discover_skills(path)
    if len(skills) != 1:
        raise MissingInstalledSkillsError([name])
    return skills[0]


def _read_prompt(skill_path: Path) -> str:
    return (skill_path / "SKILL.md").read_text(encoding="utf-8")


class AmbiguousSkillSelectionError(ValueError):
    def __init__(self, names: list[str]) -> None:
        super().__init__(f"multiple skills found; choose one with --skill: {', '.join(names)}")
