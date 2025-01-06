from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    """All paths related to building the project."""
    ROOT = Path(__file__).parent.parent.absolute()
    PYPROJECT = ROOT / "pyproject.toml"
    # Kit paths
    KIT = ROOT / "modo_kit_central"
    KIT_RESOURCES = KIT / "resources"
    KIT_DATABASE = KIT_RESOURCES / "kits.db"
    KIT_LIBS_39 = KIT / "libs_39"
    KIT_LIBS_310 = KIT / "libs_310"
    # Tooling paths
    SCRIPTS = ROOT / "scripts"
    SCRIPTS_RESOURCES = SCRIPTS / "resources"
    SCRIPT_QUERIES = SCRIPTS / "queries"
    # Data paths
    KIT_DATA = SCRIPTS_RESOURCES / "kits.json"
    AUTHOR_DATA = SCRIPTS_RESOURCES / "authors.json"


@dataclass
class KitInfo:
    """Dataclass for the kit's information."""
    name: str       # The name of the kit.
    enabled: bool   # If the kit is enabled.
    version: str    # The version of the kit.
    path: Path      # The path to the kits root directory.
