from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

@dataclass
class KitInfo:
    """Dataclass for the kit's information."""
    name: str
    enabled: bool
    version: str
    path: Path


def sanitize_hint_value(value: str) -> str:
    """Modo kit.toggleEnabled UI hints contain formatting that needs to be removed.

    Args:
        value: The UI hint value to sanitize.

    Returns:
        The sanitized UI hint value.
    """
    # Name contains UI formatting, we will need to clean it up.
    #   ([)MODO_KIT_CENTRAL(]) ([)(j:2)(c:26646166)version ([)2.0(])
    # Remove al (ETX - ASCII 3) characters from the hint name.
    sanitized_value = value.replace(chr(3), "")
    # Clear ([) and (]) from the hint name.
    #   ([)MODO_KIT_CENTRAL(]) ([)(j:2)(c:26646166)version ([)2.0(])
    sanitized_value = sanitized_value.replace("([)", "").replace("(])", "")
    # Remove the text formatting from the hint name.
    #   MODO_KIT_CENTRAL (j:2)(c:26646166)version 2.0
    sanitized_value = sanitized_value.replace("(j:2)(c:26646166)", "").strip()
    # Return the sanitized value
    #   MODO_KIT_CENTRAL version 2.0
    return sanitized_value


def hint_to_kit_info(value: str) -> KitInfo:
    """Parses the visible username text of each entry in the UI hints.

    Args:
        value: The UI hint value to parse.

    Returns:
        The parsed kit information.
    """
    # Sanitize the hint value
    sanitized_value = sanitize_hint_value(value)
    if "disabled" in sanitized_value:
        # Get the name of the kit
        sanitized_value = sanitized_value.split("(disabled)")[0].strip()
        return KitInfo(name=sanitized_value, enabled=False, version="n/a", path=None)
    else:
        # Split the value by "version" to get the name and version
        name, version = sanitized_value.split("version")
        # Return the KitInfo dataclass
        return KitInfo(name=name.strip(), enabled=True, version=version.strip(), path=None)


hint_name = "([)MODO_KIT_CENTRAL(]) ([)(j:2)(c:26646166)(])(disabled)"
clean_name = hint_to_kit_info(hint_name)
print(clean_name)

hint_name = "([)MODO_KIT_CENTRAL(]) ([)(j:2)(c:26646166)version ([)2.0(])"
clean_name = hint_to_kit_info(hint_name)
print(clean_name)

# XML data
xml_file = Path(__file__).parent.parent / "modo_kit_central" / "index.cfg"

# Parse the XML data
root = ET.parse(xml_file).getroot()

# Extract kit and version info
kit = root.attrib.get('kit')
version = root.attrib.get('version')

print(f'Kit: {kit}, Version: {version}')
