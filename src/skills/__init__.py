from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as metadata_version

from skills.hookspecs import hookimpl
from skills.manager import SkillsManager

try:
    __version__ = import_module("skills._version").version
except ModuleNotFoundError:
    try:
        __version__ = metadata_version("skills")
    except PackageNotFoundError:
        __version__ = "0.0.0"

__all__ = ["SkillsManager", "__version__", "hookimpl"]
