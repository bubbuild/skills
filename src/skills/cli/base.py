from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skills.manager import SkillsManager


@dataclass
class BaseCommand:
    name: str
    help: str
    description: str | None = None
    aliases: tuple[str, ...] = field(default_factory=tuple)

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        return None

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        raise NotImplementedError
