from __future__ import annotations

import argparse
import importlib
import pkgutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, cast

from skills.manager import SkillsManager

if TYPE_CHECKING:
    from skills.cli.base import BaseCommand


@dataclass
class State:
    cwd: Path = field(default_factory=Path.cwd)
    non_interactive: bool = False


class Core:
    def __init__(self) -> None:
        self.state = State()
        self.parser = argparse.ArgumentParser(
            prog="skills",
            description="Python-native manager for agent skills.",
        )
        self.subparsers = self.parser.add_subparsers(dest="command_name", metavar="command")
        self.commands: dict[str, BaseCommand] = {}
        self._init_parser()

    def _init_parser(self) -> None:
        self.parser.add_argument("-C", "--cwd", type=Path, help="Run as if skills started in this directory")
        self.parser.add_argument("-y", "--yes", action="store_true", help="Run without confirmation prompts")

        commands_pkg = importlib.import_module("skills.cli.commands")
        for _, name, _ in pkgutil.iter_modules(commands_pkg.__path__):
            module = importlib.import_module(f"skills.cli.commands.{name}")
            command_class = getattr(module, "Command", None)
            if command_class is not None:
                self.register_command(command_class())

    def register_command(self, command: BaseCommand) -> None:
        self.commands[command.name] = command
        parser = self.subparsers.add_parser(
            command.name,
            aliases=list(command.aliases),
            help=command.help,
            description=command.description,
        )
        command.add_arguments(parser)
        parser.set_defaults(command=command)
        for alias in command.aliases:
            self.commands[alias] = command

    def create_manager(self, cwd: Path | None = None) -> SkillsManager:
        return SkillsManager(cwd or self.state.cwd)

    def main(self, argv: list[str] | None = None) -> int:
        options = self.parser.parse_args(argv)
        if options.cwd:
            self.state.cwd = options.cwd
        self.state.non_interactive = options.yes

        command = cast("BaseCommand | None", getattr(options, "command", None))
        if command is None:
            self.parser.print_help()
            return 0

        manager = self.create_manager()
        return command.handle(manager, options)
