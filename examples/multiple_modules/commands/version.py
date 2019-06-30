import uroboros

from .root import root_cmd, print_version


class VersionCommand(uroboros.Command):
    """Print version"""

    name = 'version'
    short_description = 'Print version'
    long_description = 'Print version to stdout'

    def run(self, args):
        print_version()
        return uroboros.ExitStatus.SUCCESS


root_cmd.add_command(VersionCommand())
