from typing import Dict
from pathlib import Path
from shutil import rmtree
from zipfile import ZipFile, ZIP_DEFLATED

from .utils import Paths, make_index, get_pyproject, get_version, readable_size


def package_kit(project_data: Dict) -> Path:
    """Packages the kit into an LPK file.

    Args:
        project_data: The data from the pyproject.toml file.

    Returns:
        lpk_path: The path to the LPK file.
    """
    # Get the name of the Kit:
    kit_name = project_data['tool']['poetry']['name']
    # Get the kit directory from the project data
    kit_dir = Paths.REPO_ROOT / kit_name
    # Get the build directory
    build_dir = Paths.REPO_ROOT / "build"
    # Get the license file
    license_file = Paths.REPO_ROOT / "LICENSE"

    # Get all files in the kit directory while ignoring .pyc files
    kit_files = [f for f in kit_dir.glob("**/*") if f.is_file() and not f.suffix == ".pyc"]

    # Clear the build directory
    if build_dir.exists():
        rmtree(build_dir)
    # Remake the build directory
    build_dir.mkdir(parents=True, exist_ok=True)

    # Format the lpk file name with the version number from the VERSION file
    version = get_version(project_data)

    lpk_name = project_data['modo']['kit']['lpk_name'].format(version=version)
    lpk_path = build_dir / lpk_name
    # Message to display to the users
    user_message = f"Successfully installed {kit_name}: v{version}"

    # Build the LPK file.
    with ZipFile(lpk_path, mode='w', compression=ZIP_DEFLATED) as lpk:
        # Add the license
        lpk.write(license_file, "LICENSE")
        # Generate the index.xml file data
        index_data = make_index(folder=kit_dir, files=kit_files, message=user_message)
        # Write the index.xml file
        lpk.writestr("index.xml", index_data)

        # Write all file into the lpk
        for file in kit_files:
            print(f"Adding: {file.relative_to(kit_dir)}")
            lpk.write(file, file.relative_to(kit_dir).as_posix())

    # Get the size of the LPK file, in MB
    package_size = readable_size(lpk_path.stat().st_size, decimal=2)

    print(f"\nLPK package built: {lpk_name}")
    print(f"Package Size: {package_size}")
    return lpk_path


def main():
    """Main entry point of the builder script."""
    # Get the project details
    project = get_pyproject()

    package_kit(project)
