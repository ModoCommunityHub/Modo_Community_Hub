from typing import List
import lx, lxu

# Initialize the Host Service.
HOST_SERVICE = lx.service.Host()
# We just need the Tags.
HOST_SERVICE.SpawnForTagsOnly()
# Get a list of all package servers.
ALL_SERVERS_COUNT = HOST_SERVICE.NumServers(lx.symbol.a_PACKAGE)


def get_all_packages() -> List[str]:
    """Gets all the packages in the scene.

    Returns:
        packages: A list of all the packages in the scene.
    """
    all_packages = []

    for i in range(ALL_SERVERS_COUNT):
        factory = HOST_SERVICE.ServerByIndex(lx.symbol.a_PACKAGE, i)

        try:
            # Check to see if there is a supertype, (parent package?).
            # If this fails then we made it to the top!
            factory.InfoTag(lx.symbol.sPKG_SUPERTYPE)
            continue
        except LookupError:
            # We made it to the top of the package chain.
            # So we can add this package to the list.
            all_packages.append(factory.Name())

    return all_packages


def get_item_packages(scene_item: lxu.object.Item) -> List[str]:
    """Gets all the packages that an item contains.

    Args:
        scene_item: The item to get the packages from.

    Returns:
        item_packages: A list of all the packages attached to the item.
    """
    item_packages = []

    # Iterate over each package and test it against the scene item.
    for package in ALL_PACKAGES:
        if scene_item.PackageTest(package):
            item_packages.append(package)

    return item_packages


if __name__ == '__main__':
    # Get all available packages
    ALL_PACKAGES = get_all_packages()

    # To test this out, lets grab the default Mesh item.
    # Get the scene item to get teh Mesh item.
    scene = lxu.select.SceneSelection().current()
    # Use the ItemLookup to get the Mesh item by name.
    default_mesh = scene.ItemLookup("Mesh")
    # There will be no packages on the default Mesh item.
    # Let's add one.
    default_mesh.PackageAdd('glDraw')

    # Get a List of all the packages that the Mesh item contains.
    packages = get_item_packages(default_mesh)
    print(packages)
