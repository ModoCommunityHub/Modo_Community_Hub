import lx

from mkc.command import MKCCommand
from mkc.prefs import DATA, KIT
from mkc.lib import link_libs


class MKCLauncherCMD(MKCCommand):
    """Command to launch the Modo Kit Central window."""

    def __init__(self) -> None:
        """Initialization of the Modo Kit Central Launcher command."""
        super().__init__()

    def cmd_Flags(self) -> int:
        """Modo Override: Set the internal flags of the command.

        Notes:
            No need to undo or show the command in the event log, so we run it silently.

        Returns:
            The quiet flag
        """
        return lx.symbol.fCMD_QUIET

    def basic_Execute(self, msg: lx.object.Message, flags: int) -> None:
        """Modo Override: Launches the Material Search window.

        Args:
            msg: The commands message object
            flags: The int result of cmd_Flags()
        """
        from mkc.gui import KitCentralWindow
        if DATA.mkc_window:
            DATA.mkc_window.show()
        else:
            DATA.mkc_window = KitCentralWindow()


lx.bless(MKCLauncherCMD, KIT.CMD_LAUNCHER)
