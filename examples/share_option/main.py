from pathlib import Path

from uroboros import Command, version, Option, ExitStatus


# First, declare option class inherited from `uroboros.Option`.
class CommonOption(Option):

    def validate(self, args):
        # If there is no errors, return an empty list.
        errors = []
        if not args.path.exists():
            errors.append(Exception("'{}' does not exists.".format(args.path)))
        return errors

    def build_option(self, parser):
        parser.add_argument('path', type=Path, help="Path to show")
        parser.add_argument('-a', '--absolute', default=False,
                            action='store_true',
                            help='Show absolute path')
        return parser


class RootCommand(Command):

    name = "share_option"
    long_description = "Example of using Option"

    def build_option(self, parser):
        parser.add_argument('--version',
                            action='store_true',
                            default=False,
                            help='Print version')
        return parser

    def run(self, args):
        if args.version:
            print("{name} v{version}".format(
                name=self.name, version=version))
        else:
            self.print_help()
        return ExitStatus.SUCCESS


class DirsCommand(Command):
    """Show directories"""

    name = 'dirs'
    short_description = 'Show directories'
    long_description = 'Show directories in given path'

    # Use common option
    options = [CommonOption()]

    def run(self, args):
        p = args.path  # type:  Path
        if args.absolute and not p.is_absolute():
            p = p.expanduser().resolve()
        for path in p.iterdir():
            if path.is_dir():
                print(str(path))
        return ExitStatus.SUCCESS


class FilesCommand(Command):
    """Show files"""

    name = 'files'
    short_description = 'Show files'
    long_description = 'Show files in given path'

    # Use common option
    options = [CommonOption()]

    def build_option(self, parser):
        # Additional options
        parser.add_argument('-e', '--exclude', type=str, nargs='*',
                            metavar='EXTENSION',
                            help='File extension to hide')
        return parser

    def run(self, args):
        p = args.path  # type:  Path
        if args.absolute and not p.is_absolute():
            p = p.expanduser().resolve()
        excludes = args.exclude
        if excludes is None:
            excludes = []
        for path in p.iterdir():
            if path.is_file() and path.suffix[1:] not in excludes:
                print(str(path))
        return ExitStatus.SUCCESS


root = RootCommand()
root.add_command(DirsCommand())
root.add_command(FilesCommand())


if __name__ == '__main__':
    exit(root.execute())
