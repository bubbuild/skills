from __future__ import annotations

import argparse

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="parse",
            help="Parse a skill source string",
            description="Show how a source would be normalized before fetching.",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("source", help="Local path, owner/repo, gh:owner/repo, URL, or git URL")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        parsed = manager.parse_source(options.source)
        for key in ("kind", "url", "path", "ref", "subpath"):
            print(f"{key} = {getattr(parsed, key)}")
        return 0
