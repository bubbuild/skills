from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ParsedSource:
    raw: str
    kind: str
    url: str | None = None
    path: Path | None = None
    ref: str | None = None
    subpath: str | None = None


@dataclass(frozen=True)
class FetchedSource:
    root: Path
    source: ParsedSource
    revision: str | None = None


class EmptySourceError(ValueError):
    def __init__(self) -> None:
        super().__init__("source cannot be empty")
