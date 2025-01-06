import json
from http import HTTPStatus
from typing import Dict, Any
from urllib import request, parse

try:
    from PySide6.QtCore import QObject, Signal, qDebug
    from PySide6.QtGui import QPixmap
except ImportError:
    from PySide2.QtCore import QObject, Signal, qDebug
    from PySide2.QtGui import QPixmap

from .prefs import URLS, Paths
from .utils import up_to_date
from .database import ManifestData

class ReleaseWorker(QObject):
    """Worker class to fetch the latest release metadata from a repository."""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, repo_url: str) -> None:
        """Initialization of the ReleaseWorker.

        Args:
            repo_url: The URL to the repository.
        """
        super().__init__()
        self.repo_url = repo_url

    def run(self) -> None:
        """Runs the worker to fetch the latest release."""
        try:
            release_info = get_latest_release(self.repo_url)
            self.finished.emit(release_info)
        except Exception as e:
            self.error.emit(f"Failed to fetch the latest release: {e}")


class DatabaseWorker(QObject):
    """Worker class to fetch the latest database."""
    finished = Signal()
    error = Signal(str)

    def __init__(self) -> None:
        """Initialization of the DatabaseWorker."""
        super().__init__()
        self.manifest: ManifestData = None
        self.manifest_data: Dict[str, Any] = None
        self.manifest_url: str = None
        self.database_url: str = None
        self.assets: Dict[str, Any] = None

    def run(self) -> None:
        """Runs the worker to fetch the latest database."""
        try:
            self._update_database()
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Failed to fetch the latest database: {e}")

    def _update_database(self) -> None:
        """Initializes the database update process."""
        release_data = get_latest_release(URLS.MODO_KIT_DATABASE)
        # Extract the assets from the release data.
        self.assets = {asset['name']: asset for asset in release_data['assets']}
        # Get the manifest data from the latest release.
        self._fetch_manifest()
        self._validate_version()

    def _fetch_manifest(self) -> None:
        """Gets the manifest data from the latest release."""
        # Find the download url to the manifest.json file in the assets.
        self.manifest_url = self.assets.get('manifest.json', {}).get('browser_download_url', '')
        # Download the manifest.json data.
        with request.urlopen(self.manifest_url) as response:
            if response.status == HTTPStatus.OK:
                self.manifest_data = json.loads(response.read().decode())
                # Return the manifest data as a ManifestData object.
                self.manifest = ManifestData(**self.manifest_data)
            else:
                raise Exception(f"Failed to fetch the database manifest: {response.status}")

    def _fetch_database(self) -> None:
        """Retrieves the database file from the latest release."""
        # Get the url to the database file from the assets.
        self.database_url = self.assets.get(self.manifest.file, {}).get('browser_download_url', '')
        with request.urlopen(self.database_url) as response:
            if response.status == HTTPStatus.OK:
                # Write the database file to the resources' directory.
                Paths.DATABASE.write_bytes(response.read())
                # Since we managed to download the database, update the manifest file as well.
                Paths.DATABASE_MANIFEST.write_text(json.dumps(self.manifest_data))
            else:
                raise Exception(f"Failed to fetch the database: {response.status}")

    def _validate_version(self) -> None:
        """Validates the version of the database is up-to-date."""
        # Check if we have a local manifest file.
        if Paths.DATABASE_MANIFEST.exists():
            # Get the version from the local manifest file.
            version = json.loads(Paths.DATABASE_MANIFEST.read_text()).get('version', "0.0.0")
            # Check if the latest version is greater than the local version.
            if not up_to_date(version, self.manifest.version):
                # Download the database if the version is not up-to-date.
                self._fetch_database()
        else:
            # No local manifest file, download the database.
            self._fetch_database()


class AvatarWorker(QObject):
    """Worker class to fetch the author's avatar."""
    finished = Signal(QPixmap)
    error = Signal(str)

    def __init__(self, author: str) -> None:
        """Initialization of the AvatarWorker.

        Args:
            author: The author's name, as defined in the database, to fetch the avatar for.
        """
        super().__init__()
        self.author = author

    def run(self) -> None:
        """Runs the worker to fetch the author's avatar."""
        try:
            avatar_pixmap = self._fetch_avatar()
            self.finished.emit(avatar_pixmap)
        except Exception as e:
            self.error.emit(f"Failed to fetch the author's avatar: {e}")

    def _fetch_avatar(self) -> QPixmap:
        """Gets the author's avatar from the database.

        Returns:
            pixmap: The avatar image as a QPixmap object.
        """
        # Ensure author name is URL safe.
        url_author_name = parse.quote(self.author)
        avatar_url = URLS.AUTHOR_AVATAR.format(author=url_author_name)
        with request.urlopen(avatar_url) as response:
            if response.status == HTTPStatus.OK:
                # Load the avatar image into a QPixmap object.
                pixmap = QPixmap()
                pixmap.loadFromData(response.read())
                return pixmap
            else:
                raise Exception(f"Failed to fetch the author's avatar: {response.status}")


def get_latest_release_github(repo_url: str) -> Dict:
    """Gets the latest release manifest from the GitHub API.

    Args:
        repo_url: The URL to the repository.

    Returns:
        release: The latest release data from the GitHub API.
    """
    # Get the owner and repository name from the URL.
    # Example: https://github.com/Pixel-Fondue/modo-kit-database -> Pixel-Fondue/modo-kit-database
    owner_repo = repo_url.split(URLS.GITHUB_ROOT)[1]
    api_url = URLS.GITHUB_RELEASE_API.format(owner=owner_repo)
    # Fetch the latest release data from the GitHub API.
    with request.urlopen(api_url) as response:
        if response.status == HTTPStatus.OK:
            return json.loads(response.read())
        else:
            raise Exception(f"Failed to fetch the latest release: {response.status}")


def get_latest_release(repo_url: str) -> Dict:
    """Gets the latest database manifest file.

    Args:
        repo_url: The URL to the repository.

    Returns:
        release: The latest release data from the repositories API.
    """
    if URLS.GITHUB_ROOT in repo_url:
        return get_latest_release_github(repo_url)
    else:
        # TODO: Add support for other repository types.
        raise NotImplementedError("Only GitHub repositories are supported at this time.")
