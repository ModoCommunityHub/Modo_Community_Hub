from operator import ior
from functools import reduce

import lx
from lxu.command import BasicCommand


class MKCCommand(BasicCommand):
    """Command wrapper to add an index return when adding an argument."""

    def add_arg(self, name: str, arg_type: str, optional: bool = True, query: bool = False) -> int:
        """Adds an argument to the command and returns its index.

        Args:
            name: The name of the argument.
            arg_type: The string type of the argument.
            optional: If the argument is optional.
            query: If the argument is queryable.

        Returns:
            current_id: The index of the newly added argument.
        """
        self.dyna_Add(name, arg_type)
        current_id = self.arg_id
        flags = []
        if optional:
            flags.append(lx.symbol.fCMDARG_OPTIONAL)
        if query:
            flags.append(lx.symbol.fCMDARG_QUERY)

        # Add flags to argument. reduce with ior == flag | flag | ...
        self.dyna_SetFlags(current_id, reduce(ior, flags))
        self.arg_id += 1

        return current_id
