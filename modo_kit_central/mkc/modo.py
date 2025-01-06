from typing import Dict, Iterator
from pathlib import Path
from xml.etree import ElementTree as ET

import lxu

from .prefs import DATA, KitInfo, ImportInfo


def get_command_ui_hints(command: str) -> lxu.object.UIValueHints:
    """Gets the UI Values Hints for the given command.

    Args:
        command: The string command to get the UI hints for.
    """
    # Get the command service to spawn the command.
    service_command = lxu.service.Command()
    # Spawn the command to get the UI hints.
    _, _, command_object = service_command.SpawnFromString(command)
    # Get the Attributes UI from the command object.
    attributes_ui = lxu.object.AttributesUI(command_object)
    # Get the UI hints for the command.
    ui_value_hints = attributes_ui.UIValueHints(0)

    return ui_value_hints


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


def hint_to_kit_info(value: str, import_data: Dict[str, ImportInfo]) -> KitInfo:
    """Parses the visible username text of each entry in the UI hints.

    Args:
        value: The UI hint value to parse.
        import_data: The data from the index.cfg files.

    Returns:
        The parsed kit information.
    """
    # Sanitize the hint value
    sanitized_value = sanitize_hint_value(value)
    if "(disabled)" in sanitized_value:
        # Get the name of the kit
        sanitized_value = sanitized_value.split("(disabled)")[0].strip()
        # Version is not available for disabled kits, so we need to get it from the index.cfg file.
        import_info = import_data.get(sanitized_value)
        return KitInfo(name=sanitized_value, enabled=False, version=import_info.name, path=import_info.path)
    else:
        # Split the value by "version" to get the name and version
        name, version = sanitized_value.split("version")
        # Get the path from the import data.
        import_info = import_data.get(name.strip())
        # Return the KitInfo dataclass
        return KitInfo(name=name.strip(), enabled=True, version=version.strip(), path=import_info.path)


def populate_installed_kits() -> None:
    """Gets all kits recognized by the users current Modo session."""
    # Initialize the modo_kits dictionary
    DATA.modo_kits = {}

    # Get all import paths that contain an 'index.cfg' file.
    # We use this to determine the version of a kit if it is disabled.
    import_data = get_import_data()

    # Get the UI value hints for kit.toggleEnable to check all kits enabled status.
    ui_value_hints = get_command_ui_hints("kit.toggleEnable")
    for hint_index in range(ui_value_hints.PopCount()):
        # Get the hint value at the given index.
        ui_value_hint = ui_value_hints.PopUserName(hint_index)
        # Convert the hint into a KitInfo.
        kit_info = hint_to_kit_info(ui_value_hint, import_data)
        # Add kit info to the modo_kits data.
        DATA.modo_kits[kit_info.name] = kit_info


def get_import_data() -> Dict[str, ImportInfo]:
    """Extracts the data from the index.cfg files for all installed kits.

    Returns:
        Dict[str, str]: A dictionary of installed kit names and versions.
    """
    kit_xml_data = {}

    for kit_config_file in all_imported_kits():
        try:
            # Parse the XML data from the index.cfg file.
            configuration = ET.parse(kit_config_file).getroot()
            # <configuration kit="MODO_KIT_CENTRAL" version="1.30" and="rel]1500"></configuration>
            kit_name = configuration.attrib.get('kit')
            kit_version = configuration.attrib.get('version')
            kit_root_path = kit_config_file.parent
            kit_xml_data[kit_name] = ImportInfo(name=kit_name, version=kit_version, path=kit_root_path)
        except ET.ParseError:
            print(f"Error parsing {kit_config_file.parent.name}/index.cfg")

    return kit_xml_data


def all_imported_kits() -> Iterator[Path]:
    """Finds all the index.cfg paths to the installed kits.

    Returns:
        Iterator[Path]: An iterator of all the index.cfg files.
    """
    platform_srv = lxu.service.Platform()
    # Iterate over all import paths available to the current Modo session.
    for path_index in range(platform_srv.ImportPathCount()):
        # Get the import path as a Path object.
        import_path = Path(platform_srv.ImportPathByIndex(path_index))
        # Iterate over all items in the import path.
        for import_item in import_path.iterdir():
            if import_item.is_file() and import_item.name.lower() == "index.cfg":
                # We found an index! yield it.
                yield import_item
            elif import_item.is_dir():
                # Only check 1 level down for an index.cfg
                for sub_import_item in import_item.iterdir():
                    if sub_import_item.name.lower() == "index.cfg":
                        # We found an index! yield it.
                        yield sub_import_item
