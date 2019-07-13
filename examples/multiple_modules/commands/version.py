import uroboros

from .root import print_version


class VersionCommand(uroboros.Command):
    """Print version"""

    name = 'version'
    short_description = 'Print version'
    long_description = 'Print version to stdout'

    def run(self, args):
        print_version()
        return uroboros.ExitStatus.SUCCESS


command = VersionCommand()
