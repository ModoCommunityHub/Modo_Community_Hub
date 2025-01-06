import json
from pathlib import Path

from .prefs import Paths, DATA


def load_resource(res_type: str) -> dict:
    """Loads a given resource from the resources' directory.

    Args:
        res_type: The resource type to load

    Returns:
        The loaded resource.
    """
    resource = Paths.RESOURCES / f"{res_type}.json"

    if resource.exists():
        with resource.open('r') as resource_file:
            return json.load(resource_file)
    else:
        return {}


def set_absolute_images(css_data: str) -> str:
    """Sets the absolute path for images in the CSS.

    Args:
        css_data: The CSS data to update.
    """
    return css_data.replace("url(", f"url({Paths.IMAGES_CSS.as_posix()}/")


def load_stylesheet() -> None:
    """Leads the stylesheet used for the QT widgets."""
    style_path = Paths.RESOURCES / "style.css"
    # Load the css file into the data object.
    DATA.CSS = set_absolute_images(style_path.read_text())

    if DATA.local:
        # Load CSS from repo resources
        repo_resources = Paths.KIT_ROOT.parent / "scripts" / "resources"
        repo_style_path = repo_resources / "style.css"
        # pre-pend css data to the kit css data
        DATA.CSS = set_absolute_images(repo_style_path.read_text()) + DATA.CSS


def load_avatar(avatar: str) -> Path:
    """Gets the avatar image from the resources' directory.

    Args:
        avatar: The file name of the avatar to load.

    Returns:
        resource: Path to the avatar file or None if it doesn't exist.
    """
    if isinstance(avatar, int):
        avatar = False
    avatar = avatar if avatar else "profile.png"
    resource = Paths.RESOURCES / "avatars" / avatar

    if resource.exists():
        return resource


def up_to_date(version_local: str, version_latest: str) -> bool:
    """Compares two version strings.

    Args:
        version_local: The local version string.
        version_latest: The latest version string.
    """
    try:
        local_version = [int(v) for v in version_local.split(".")]
        latest_version = [int(v) for v in version_latest.split(".")]
    except ValueError:
        # Version is corrupted, assume it's out-of-date, update required.
        return False

    if local_version < latest_version:
        # Local version is out-of-date, update required.
        return False
    else:
        # Local version is up-to-date.
        return True