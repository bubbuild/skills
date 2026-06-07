from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import platformdirs
import tomli_w

from skills._compat import tomllib


def ensure_boolean(value: Any) -> bool:
    if not isinstance(value, str):
        return bool(value)
    return bool(value) and value.lower() not in {"0", "false", "no", "off"}


def split_csv(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return list(value)


def normalize_install_mode(value: Any) -> str:
    return str(value).lower()


@dataclass(frozen=True)
class ConfigItem:
    description: str
    default: Any
    global_only: bool = False
    coerce: Callable[[Any], Any] = str


@dataclass(frozen=True)
class ConfigSource:
    name: str
    path: Path
    data: dict[str, Any]
    exists: bool
    blocks_lower_priority: bool = False
    project: bool = True
    wrapper: str | None = None


class GlobalOnlyConfigError(ValueError):
    def __init__(self, key: str) -> None:
        super().__init__(f"{key!r} is only valid in global configuration")


def load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        return {}


def flatten_values(data: Mapping[str, Any]) -> dict[str, Any]:
    def flatten(prefix: str, values: Mapping[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values.items():
            next_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, Mapping):
                result.update(flatten(next_key, value))
            else:
                result[next_key] = value
        return result

    return flatten("", data)


def _flatten_tool_skills(data: Mapping[str, Any]) -> dict[str, Any]:
    section = data.get("tool", {}).get("skills", {})
    return flatten_values(section) if isinstance(section, Mapping) else {}


def _assign_nested(data: dict[str, Any], parts: list[str], value: Any) -> None:
    current = data
    for part in parts[:-1]:
        nested = current.setdefault(part, {})
        if not isinstance(nested, dict):
            nested = {}
            current[part] = nested
        current = nested
    current[parts[-1]] = value


def unflatten_values(values: Mapping[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key, value in values.items():
        if isinstance(value, Mapping):
            _assign_nested(data, key.split("."), dict(value))
        else:
            _assign_nested(data, key.split("."), value)
    return data


def _unflatten_tool_skills(values: Mapping[str, Any]) -> dict[str, Any]:
    return {"tool": {"skills": unflatten_values(values)}}


class Config(MutableMapping[str, Any]):
    _items: ClassVar[dict[str, ConfigItem]] = {
        "cache_dir": ConfigItem(
            "Root directory for fetched skill sources",
            platformdirs.user_cache_path("skills").as_posix(),
            global_only=True,
        ),
        "state_dir": ConfigItem(
            "Root directory for lock files and installed state",
            platformdirs.user_state_path("skills").as_posix(),
            global_only=True,
        ),
        "install.mode": ConfigItem(
            "Default install mode, either symlink or copy",
            "symlink",
            coerce=normalize_install_mode,
        ),
        "agents": ConfigItem(
            "Default target agents",
            ["agents"],
            coerce=split_csv,
        ),
    }

    def __init__(
        self,
        path: Path,
        *,
        project: bool = False,
        data: dict[str, Any] | None = None,
        wrapper: str | None = None,
    ) -> None:
        self.path = path
        self.project = project
        self.wrapper = wrapper
        if data is not None:
            self._data = dict(data)
        else:
            raw = load_toml(path)
            self._data = self._flatten_raw(raw)

    @classmethod
    def from_source(cls, source: ConfigSource) -> Config:
        return cls(
            source.path,
            project=source.project,
            data=source.data,
            wrapper=source.wrapper,
        )

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return {key: item.default for key, item in cls._items.items()}

    @property
    def data(self) -> dict[str, Any]:
        return dict(self._data)

    def __getitem__(self, key: str) -> Any:
        item = self._items.get(key)
        if key in self._data:
            value = self._data[key]
        elif item is not None:
            value = item.default
        else:
            raise KeyError(key)
        return item.coerce(value) if item else value

    def __setitem__(self, key: str, value: Any) -> None:
        item = self._items.get(key)
        if self.project and item and item.global_only:
            raise GlobalOnlyConfigError(key)
        self._data[key] = item.coerce(value) if item else value
        self.save()

    def __delitem__(self, key: str) -> None:
        del self._data[key]
        self.save()

    def __iter__(self) -> Iterator[str]:
        yield from sorted(set(self._items) | set(self._data))

    def __len__(self) -> int:
        return len(set(self._items) | set(self._data))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._unflatten_data()
        self.path.write_text(tomli_w.dumps(payload), encoding="utf-8")

    def _flatten_raw(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        if self.wrapper == "tool.skills":
            return _flatten_tool_skills(raw)
        if self.project:
            return flatten_values(raw)
        return dict(raw)

    def _unflatten_data(self) -> dict[str, Any]:
        if self.wrapper == "tool.skills":
            return _unflatten_tool_skills(self._data)
        if self.project:
            return unflatten_values(self._data)
        return dict(self._data)


@dataclass
class ConfigStack:
    global_config: Config
    project_config: Config
    fallback_project_configs: list[Config] = field(default_factory=list)

    def get(self, key: str) -> Any:
        if key in self.project_config.data:
            return self.project_config[key]
        for config in self.fallback_project_configs:
            if key in config.data:
                return config[key]
        if key in self.global_config.data:
            return self.global_config[key]
        return Config._items[key].default

    def resolved(self) -> dict[str, Any]:
        values = Config.defaults()
        values.update(self.global_config.data)
        for config in reversed(self.fallback_project_configs):
            values.update(config.data)
        values.update(self.project_config.data)
        return values
