import sys
import shutil
from pathlib import Path

import toml


def install(project: dict) -> None:
    """Installs the development kit into the modo kits directory.

    Args:
        project: The pyproject.toml data.
    """
    # Get the root path `~/modo-kit-central/`
    repo_dir = Path().absolute()

    # Get the os dependant kits path
    if sys.platform == "win32":
        install_path = Path(r"~\AppData\Roaming\Luxology\Kits").expanduser()
    elif sys.platform == "darwin":
        install_path = Path("~/Library/Application Support/Luxology/Kits").expanduser()
    else:
        raise ValueError(f"Unsupported platform: {sys.platform}")

    # Get the name of the kits directory
    kit_name = project['project']['name']
    # Get the development kit.
    kit_path = repo_dir / kit_name
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


if __name__ == '__main__':
    # Load the pyproject
    pyproject = toml.load("pyproject.toml")

    install(pyproject)
