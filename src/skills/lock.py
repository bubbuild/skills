from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import tomli_w

from skills._compat import tomllib

LOCK_FORMAT_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


@dataclass(frozen=True)
class LockMetadata:
    lock_version: str = LOCK_FORMAT_VERSION
    generated_by: str = "skills"

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> LockMetadata:
        return cls(
            lock_version=str(data["lock_version"]),
            generated_by=str(data.get("generated_by", "skills")),
        )

    def to_data(self) -> dict[str, str]:
        return {
            "lock_version": self.lock_version,
            "generated_by": self.generated_by,
        }


@dataclass(frozen=True)
class LockEntry:
    name: str
    source: str
    source_kind: str
    source_url: str | None
    source_ref: str | None
    source_revision: str | None
    source_subpath: str | None
    skill_path: str
    content_hash: str
    install_mode: str
    targets: list[str]
    installed_at: str
    updated_at: str

    @classmethod
    def from_data(cls, name: str, data: dict[str, Any]) -> LockEntry:
        return cls(
            name=name,
            source=str(data["source"]),
            source_kind=str(data["source_kind"]),
            source_url=_optional_str(data.get("source_url")),
            source_ref=_optional_str(data.get("source_ref")),
            source_revision=_optional_str(data.get("source_revision")),
            source_subpath=_optional_str(data.get("source_subpath")),
            skill_path=str(data["skill_path"]),
            content_hash=str(data["content_hash"]),
            install_mode=str(data["install_mode"]),
            targets=[str(target) for target in data.get("targets", [])],
            installed_at=str(data["installed_at"]),
            updated_at=str(data["updated_at"]),
        )

    def to_data(self) -> dict[str, Any]:
        data = {
            "source": self.source,
            "source_kind": self.source_kind,
            "skill_path": self.skill_path,
            "content_hash": self.content_hash,
            "install_mode": self.install_mode,
            "targets": self.targets,
            "installed_at": self.installed_at,
            "updated_at": self.updated_at,
        }
        if self.source_url is not None:
            data["source_url"] = self.source_url
        if self.source_ref is not None:
            data["source_ref"] = self.source_ref
        if self.source_revision is not None:
            data["source_revision"] = self.source_revision
        if self.source_subpath is not None:
            data["source_subpath"] = self.source_subpath
        return data


@dataclass
class SkillLock:
    path: Path
    metadata: LockMetadata = field(default_factory=LockMetadata)
    entries: dict[str, LockEntry] = field(default_factory=dict)

    @classmethod
    def read(cls, path: Path) -> SkillLock:
        try:
            with path.open("rb") as file:
                data = tomllib.load(file)
        except FileNotFoundError:
            return cls(path=path)

        metadata = LockMetadata.from_data(data["metadata"])
        raw_entries = data.get("skill", {})
        entries = {
            name: LockEntry.from_data(name, entry) for name, entry in raw_entries.items() if isinstance(entry, dict)
        }
        return cls(path=path, metadata=metadata, entries=entries)

    def set(self, entry: LockEntry) -> None:
        self.entries[entry.name] = entry

    def remove(self, name: str) -> LockEntry | None:
        return self.entries.pop(name, None)

    def is_empty(self) -> bool:
        return not self.entries

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "metadata": self.metadata.to_data(),
            "skill": {name: entry.to_data() for name, entry in sorted(self.entries.items())},
        }
        self.path.write_text(tomli_w.dumps(payload), encoding="utf-8")
