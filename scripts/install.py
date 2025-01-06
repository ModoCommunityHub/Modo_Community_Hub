import sys
import shutil
from typing import Dict
from pathlib import Path

import toml

from .prefs import Paths


def install(project: Dict) -> None:
    """Installs the development kit into the modo kits directory.

    Args:
        project: The pyproject.toml data.

    Raises:
        ValueError: If the platform is not supported.
    """
    # Get the os dependant kits path
    if sys.platform == "win32":
        install_path = Path(r"~\AppData\Roaming\Luxology\Kits").expanduser()
    elif sys.platform == "darwin":
        install_path = Path("~/Library/Application Support/Luxology/Kits").expanduser()
    else:
        raise ValueError(f"Unsupported platform: {sys.platform}")

    # Get the name of the kits directory
    kit_name = project['tool']['poetry']['name']
    # Get the development kit.
    kit_path = Paths.ROOT / kit_name
    # Get the modo install path for kit
    modo_kit_path = install_path / kit_name

    # If the Kit exists in the modo kit path, remove it before copying the new one.
    if modo_kit_path.exists():
        print("Removing old kit...")
        shutil.rmtree(modo_kit_path)

    print("Copying new kit data...")
    # Copy the development kit to the modo kit path.
    shutil.copytree(src=kit_path, dst=modo_kit_path)
    print("Installation complete.")


def main() -> None:
    """Main entry point of the installer script."""
    # Load the pyproject.toml file and pass it to the installer.
    pyproject = toml.load("pyproject.toml")

    install(pyproject)
