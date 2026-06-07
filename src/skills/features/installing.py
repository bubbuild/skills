from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from skills.features.discovery import Skill, discover_skills
from skills.features.names import index_skills_by_normalized_name, normalize_skill_name
from skills.lock import LockEntry, SkillLock, utc_now
from skills.project import Project
from skills.source import FetchedSource

CANONICAL_DIR = ".skills"
INSTALLED_DIR = "installed"
LOCK_FILE = "skills.lock"


@dataclass(frozen=True)
class InstallOptions:
    source: str
    selected_skills: list[str]
    targets: list[str]
    mode: str
    global_install: bool = False
    refresh: bool = False


@dataclass(frozen=True)
class InstallResult:
    skill: Skill
    canonical_path: Path
    target_paths: list[Path]
    lock_entry: LockEntry


@dataclass(frozen=True)
class RemoveOptions:
    names: list[str]
    global_install: bool = False


@dataclass(frozen=True)
class UpdateOptions:
    names: list[str]
    global_install: bool = False


@dataclass(frozen=True)
class RemoveResult:
    name: str
    canonical_path: Path
    target_paths: list[Path]


class MissingSkillsError(ValueError):
    def __init__(self, names: list[str]) -> None:
        super().__init__(f"skills not found: {', '.join(names)}")


class MissingInstalledSkillsError(ValueError):
    def __init__(self, names: list[str]) -> None:
        super().__init__(f"installed skills not found: {', '.join(names)}")


class InvalidInstallModeError(ValueError):
    def __init__(self, mode: str) -> None:
        super().__init__(f"install mode must be symlink or copy, got {mode!r}")


def hash_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = file.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def state_root(project: Project, *, global_install: bool) -> Path:
    if global_install:
        state_dir = Path(str(project.config.get("state_dir"))).expanduser()
        return state_dir
    return project.root / CANONICAL_DIR


def project_lock_path(project: Project, *, global_install: bool) -> Path:
    return state_root(project, global_install=global_install) / LOCK_FILE


def canonical_root(project: Project, *, global_install: bool) -> Path:
    return state_root(project, global_install=global_install) / INSTALLED_DIR


def install_from_source(project: Project, options: InstallOptions) -> list[InstallResult]:
    hooks = project.require_hooks()
    parsed = hooks.parse_source(options.source)
    fetched = hooks.fetch_source(parsed, project, refresh=options.refresh)
    skills = _select_skills(discover_skills(fetched.root), options.selected_skills)
    lock = SkillLock.read(project_lock_path(project, global_install=options.global_install))

    results = [_install_skill(project, fetched, skill, options, lock) for skill in skills]
    lock.save()
    return results


def remove_installed(project: Project, options: RemoveOptions) -> list[RemoveResult]:
    hooks = project.require_hooks()
    lock = SkillLock.read(project_lock_path(project, global_install=options.global_install))
    names = _locked_names(lock, options.names)
    missing = sorted(set(names) - set(lock.entries))
    if missing:
        raise MissingInstalledSkillsError(missing)

    results = []
    for name in names:
        entry = lock.remove(name)
        if entry is None:
            continue
        canonical_path = Path(entry.skill_path)
        target_paths = [
            hooks.install_target(target, project, global_install=options.global_install) / name
            for target in entry.targets
        ]
        for target_path in target_paths:
            _remove_path(target_path)
        _remove_path(canonical_path)
        results.append(RemoveResult(name=name, canonical_path=canonical_path, target_paths=target_paths))

    lock.save()
    return results


def update_installed(project: Project, options: UpdateOptions) -> list[InstallResult]:
    lock = SkillLock.read(project_lock_path(project, global_install=options.global_install))
    names = _locked_names(lock, options.names, default_all=True)
    missing = sorted(set(names) - set(lock.entries))
    if missing:
        raise MissingInstalledSkillsError(missing)

    results = []
    for name in names:
        entry = lock.entries[name]
        results.extend(
            install_from_source(
                project,
                InstallOptions(
                    source=entry.source,
                    selected_skills=[name],
                    targets=entry.targets,
                    mode=entry.install_mode,
                    global_install=options.global_install,
                    refresh=True,
                ),
            )
        )
    return results


def _select_skills(skills: list[Skill], selected: list[str]) -> list[Skill]:
    by_name = index_skills_by_normalized_name(skills)
    if not selected or selected == ["*"]:
        return skills

    requested = [normalize_skill_name(name) for name in selected]
    missing = sorted(set(requested) - set(by_name))
    if missing:
        raise MissingSkillsError(missing)
    return [by_name[name] for name in requested]


def _locked_names(lock: SkillLock, requested_names: list[str], *, default_all: bool = False) -> list[str]:
    if requested_names == ["*"] or (default_all and not requested_names):
        return sorted(lock.entries)
    return [normalize_skill_name(name) for name in requested_names]


def _install_skill(
    project: Project,
    fetched: FetchedSource,
    skill: Skill,
    options: InstallOptions,
    lock: SkillLock,
) -> InstallResult:
    name = normalize_skill_name(skill.name)
    canonical_path = canonical_root(project, global_install=options.global_install) / name
    _replace_tree(skill.path, canonical_path)

    hooks = project.require_hooks()
    target_paths = []
    for target_name in options.targets:
        target_root = hooks.install_target(target_name, project, global_install=options.global_install)
        target_path = target_root / name
        _install_target(canonical_path, target_path, options.mode)
        target_paths.append(target_path)

    now = utc_now()
    previous = lock.entries.get(name)
    source = fetched.source
    entry = LockEntry(
        name=name,
        source=options.source,
        source_kind=source.kind,
        source_url=source.url,
        source_ref=source.ref,
        source_revision=fetched.revision,
        source_subpath=source.subpath,
        skill_path=canonical_path.as_posix(),
        content_hash=hash_directory(canonical_path),
        install_mode=options.mode,
        targets=options.targets,
        installed_at=previous.installed_at if previous else now,
        updated_at=now,
    )
    lock.set(entry)
    return InstallResult(skill=skill, canonical_path=canonical_path, target_paths=target_paths, lock_entry=entry)


def _replace_tree(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, symlinks=True)


def _install_target(canonical_path: Path, target_path: Path, mode: str) -> None:
    if target_path.exists() or target_path.is_symlink():
        if target_path.is_dir() and not target_path.is_symlink():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if mode == "copy":
        shutil.copytree(canonical_path, target_path, symlinks=True)
        return
    if mode != "symlink":
        raise InvalidInstallModeError(mode)

    try:
        target_path.symlink_to(canonical_path.resolve(), target_is_directory=True)
    except OSError:
        shutil.copytree(canonical_path, target_path, symlinks=True)


def _remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()
