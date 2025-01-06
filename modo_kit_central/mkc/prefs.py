import sys
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .gui import KitCentralWindow

PY_VERSION = f"{sys.version_info.major}{sys.version_info.minor}"


@dataclass
class KitInfo:
    """Dataclass for the kit's information."""
    name: str       # The name of the kit.
    enabled: bool   # If the kit is enabled.
    version: str    # The version of the kit.
    path: Path      # The path to the kits root directory.


@dataclass
class ImportInfo:
    """Dataclass for the import information."""
    name: str       # The name of the kit.
    version: str    # The version of the kit.
    path: Path      # The path to the kits root directory.


@dataclass
class DATA:
    """Dataclass for storing live data while the kit is running."""
    local: bool = False
    resources: Path = None
    authors: Dict = None
    CSS: str = ""
    mkc_window: 'KitCentralWindow' = None
    modo_kits: Dict[str, KitInfo] = None


class Paths:
    """Paths for Modo Kit Central resources."""
    KIT_ROOT = Path(__file__).parent.parent.absolute()
    KIT_LIBS = KIT_ROOT / f"libs_{PY_VERSION}"
    RESOURCES = KIT_ROOT / "resources"
    DATABASE = RESOURCES / "mkc_kits.db"
    DATABASE_MANIFEST = RESOURCES / "manifest.json"
    TEST_RELEASE = RESOURCES / "test_release.json"
    AVATAR = RESOURCES / "avatars" / "profile.png"
    IMAGES = RESOURCES / "images"
    ICON = IMAGES / "icon.png"
    IMAGES_CSS = IMAGES / "css"
    BANNERS = IMAGES / "banners"
    BANNER_MKC = BANNERS / "Modo Kit Central.png"


@dataclass
class URLS:
    """Dataclass for storing URL information."""
    GITHUB_ROOT = "github.com/"
    MODO_KIT_DATABASE = "https://github.com/Pixel-Fondue/modo-kit-database"
    GITHUB_RELEASE_API = "https://api.github.com/repos/{owner}/releases/latest"
    AUTHOR_AVATAR = "https://raw.githubusercontent.com/Pixel-Fondue/modo-kit-database/refs/heads/main/kits/{author}/avatar.png"

class Text:
    """Dataclass for storing text information."""
    title = "Modo Kit Central"
    author = "Author: <a href='{}' style='color: white'>{}</a>"
    lbl_link = "<a href='{link}' style='color: white'>{text}</a>"
    info_block = (
        "Welcome to Modo Kit Central! aka MKC\n\n"
        "MKC is a tool to help you find and install kits for Modo."
        "Currently, MKC only supports free kits. If you are a Kit Author that"
        "would like to onboard your kits, Reach out to PF for more info."
        "Pixel Fondue is working hard"
        "to onboard paid kits as well. Stay tuned for updates!"
    )


class KEYS:
    """Keys for the different tabs."""
    KITS = "Kits"
    AUTHORS = "Authors"
    INFO = "Info"


class KIT:
    """Constants for the Kit Central."""
    ABV = "mkc"
    NAME = "modo_kit_central"
    NICE_NAME = "Modo Kit Central"
    CMD_LAUNCHER = f"{ABV}.launcher"


@dataclass
class KitData:
    """Dataclass for the kit's information."""
    id: int             # The id of the kit within the database.
    name: str           # The name attribute from the index.cfg.
    label: str          # The nice name of the kit to display.
    author: str         # The original author of the kit.
    version: str        # The current version of the kit.
    description: str    # The description of the kit for users.
    search: List[str]   # The search terms for the kit.
    # The following fields are optional.
    url: str = None             # The URL to the kit's homepage.
    help: str = None            # The URL to the kit's help page.
    manifest: str = None        # The manifest.json file for the kit installation.
    has_banner: bool = False    # If the kit has a banner image.
    installable: bool = False   # If the kit is installable via MKC.

    # Search will come in as a comma separated string, so we need to convert it to a list.
    def __post_init__(self) -> None:
        """Convert the search string to a list."""
        self.search = self.search.split(",") if self.search else []


@dataclass
class AuthorData:
    """Dataclass for the author's information."""
    id: int     # The id of the author within the database.
    name: str   # The name of the author.
    # The following fields are optional.
    avatar: bool = False            # Whether the author has an avatar to display.
    handle: str = None              # The author's handle.
    links: Dict[str, str] = None    # A JSON object containing links to the author's social media.

    def __post_init__(self):
        """Convert the links json string to a dictionary."""
        if self.links is not None:
            self.links = json.loads(self.links) if self.links else {}


@dataclass
class QueryData:
    """Dataclass for the query data."""
    SelectKits: str = "SELECT * FROM kits WHERE TRUE"
    SearchTerm: str = " AND (name LIKE ? OR author LIKE ? OR search LIKE ? OR Description LIKE ?)"
    SelectAuthor: str = "SELECT * FROM authors WHERE name LIKE ?"
    SelectKitsByAuthor: str = "SELECT * FROM kits WHERE author = ?"
