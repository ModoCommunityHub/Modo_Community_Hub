from dataclasses import dataclass
from typing import List
import sqlite3

from .prefs import Paths, KitData, AuthorData, QueryData


@dataclass
class ManifestData:
    """Dataclass for the release information from the manifest.json file."""
    version: str    # The version of the database.
    file: str       # The name of the database file.


def search_kits(search_text: str) -> List[int]:
    """Searches the database for the given search text.

    Args:
        search_text: The text to search for.
    """
    # Split the search text into individual terms.
    search_terms = [s.strip() for s in search_text.split(",")]

    # Generate the search query for all terms.
    query = QueryData.SelectKits
    params = []

    for term in search_terms:
        query += QueryData.SearchTerm
        # For every '?' in the query, add the search term to the params.
        params.extend([f"%{term}%"] * QueryData.SearchTerm.count("?"))

    with sqlite3.connect(Paths.DATABASE) as connection:
        cursor = connection.cursor()
        # Search all fields in kits table for the search text.
        cursor.execute(query, params)
        # Get id of all matching kits and remap from 1-indexed to 0-indexed.
        return [kit[0] - 1 for kit in cursor.fetchall()]


def get_kits() -> List[KitData]:
    """Gets all kits from the database.

    Returns:
        kits: A list of all kits in the database.
    """
    with sqlite3.connect(Paths.DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(QueryData.SelectKits)
        return [KitData(*k) for k in cursor.fetchall()]


def get_author(author: str) -> AuthorData:
    """Gets the author data from the database.

    Args:
        author: The author's name to get data for.

    Returns:
        author_data: The author's data class.
    """
    search_params = [f"%{author}%"]

    with sqlite3.connect(Paths.DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(QueryData.SelectAuthor, search_params)
        return AuthorData(*cursor.fetchone())


def get_author_kits(author: str) -> List[KitData]:
    """Gets all kits from the database by the given author.

    Args:
        author: The author's name to get data for.

    Returns:
        A list of all kits by the author.
    """
    with sqlite3.connect(Paths.DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(QueryData.SelectKitsByAuthor, [author])
        return [KitData(*k) for k in cursor.fetchall()]
