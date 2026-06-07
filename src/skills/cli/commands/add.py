from __future__ import annotations

import argparse

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="add",
            help="Install skills from a source",
            description="Install local or Git-backed skills into canonical storage and configured targets.",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("source", help="Local path, GitHub shorthand, GitHub URL, or git URL")
        parser.add_argument("-s", "--skill", action="append", default=[], help="Skill name to install")
        parser.add_argument("-a", "--agent", action="append", default=[], help="Install target name")
        parser.add_argument("-g", "--global", dest="global_install", action="store_true", help="Install globally")
        parser.add_argument("--copy", action="store_true", help="Copy instead of symlinking to targets")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        results = manager.add(
            options.source,
            skills=options.skill,
            targets=options.agent or None,
            mode="copy" if options.copy else None,
            global_install=options.global_install,
        )
        for result in results:
            targets_text = ", ".join(path.as_posix() for path in result.target_paths)
            print(f"{result.lock_entry.name} -> {targets_text}")
        return 0
