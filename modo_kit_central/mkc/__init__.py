from os import environ

from .utils import load_stylesheet, load_resource
from .version import version
from .prefs import DATA

__version__ = version

# Check if running in local mode by grabbing the MKC_LOCAL environment variable
DATA.local = True if "MKC_LOCAL" in environ else False


if DATA.local:
    # Populate mock data in DATA.modo_kits
    ...
else:
    from .modo import populate_installed_kits
    populate_installed_kits()


# Load and configure the CSS stylesheet.
load_stylesheet()
