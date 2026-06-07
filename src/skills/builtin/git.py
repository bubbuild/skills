from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from skills.hookspecs import hookimpl
from skills.project import Project
from skills.source import FetchedSource, ParsedSource


def _split_ref(value: str) -> tuple[str, str | None]:
    if "@" not in value:
        return value, None
    left, right = value.rsplit("@", 1)
    return left, right or None


class GitSourcePlugin:
    @hookimpl
    def parse_source(self, raw: str) -> ParsedSource | None:
        value = raw.strip()
        if not value:
            return None

        if value.startswith(("file:", "./", "../", "/")) or value in {".", ".."}:
            path = value[5:] if value.startswith("file:") else value
            return ParsedSource(raw=value, kind="local", path=Path(path).expanduser())

        if value.startswith("gh:"):
            repo, ref = _split_ref(value[3:])
            return ParsedSource(raw=value, kind="git", url=f"https://github.com/{repo}.git", ref=ref)

        if value.startswith("git@"):
            return ParsedSource(raw=value, kind="git", url=value)

        parsed = urlparse(value)
        if parsed.scheme in {"http", "https"} and parsed.netloc == "github.com":
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) < 2:
                return None
            owner_repo = "/".join(parts[:2]).removesuffix(".git")
            ref = None
            subpath = None
            if len(parts) >= 4 and parts[2] == "tree":
                ref = parts[3]
                subpath = "/".join(parts[4:]) or None
            return ParsedSource(
                raw=value,
                kind="git",
                url=f"https://github.com/{owner_repo}.git",
                ref=ref,
                subpath=subpath,
            )

        if parsed.scheme in {"http", "https", "ssh", "git"}:
            return ParsedSource(raw=value, kind="git", url=value)

        source, ref = _split_ref(value)
        if source.count("/") == 1:
            return ParsedSource(raw=value, kind="git", url=f"https://github.com/{source}.git", ref=ref)

        return ParsedSource(raw=value, kind="local", path=Path(value).expanduser())

    @hookimpl
    def fetch_source(self, source: ParsedSource, project: Project, refresh: bool) -> FetchedSource | None:
        if source.kind == "local" and source.path is not None:
            path = source.path if source.path.is_absolute() else project.root / source.path
            root = path / source.subpath if source.subpath else path
            return FetchedSource(root=root, source=source)
        if source.kind == "git" and source.url is not None:
            root = _clone_to_cache(source, project, refresh=refresh)
            source_root = root / source.subpath if source.subpath else root
            return FetchedSource(root=source_root, source=source, revision=_git_revision(root))
        return None


class GitExecutableNotFoundError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("git executable was not found")


class GitFetchError(RuntimeError):
    def __init__(self, url: str, stderr: str) -> None:
        super().__init__(f"failed to fetch git source {url}: {stderr.strip()}")


class GitSourceUrlMissingError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("git source URL is missing")


def _clone_to_cache(source: ParsedSource, project: Project, *, refresh: bool) -> Path:
    if source.url is None:
        raise GitSourceUrlMissingError()
    git = _find_git()

    cache_key = hashlib.sha256(f"{source.url}@{source.ref or ''}".encode()).hexdigest()[:16]
    cache_root = Path(str(project.config.get("cache_dir"))).expanduser() / "git" / cache_key
    if refresh and cache_root.exists():
        shutil.rmtree(cache_root)
    if cache_root.exists():
        return cache_root

    cache_root.parent.mkdir(parents=True, exist_ok=True)
    command = [git, "clone", "--depth", "1"]
    if source.ref:
        command.extend(["--branch", source.ref])
    command.extend([source.url, str(cache_root)])

    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise GitFetchError(source.url, result.stderr)
    return cache_root


def _find_git() -> str:
    git = shutil.which("git")
    if git is None:
        raise GitExecutableNotFoundError()
    return git


def _git_revision(root: Path) -> str | None:
    git = _find_git()
    result = subprocess.run([git, "-C", str(root), "rev-parse", "HEAD"], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None
