from uroboros import Command, version
from uroboros.constants import ExitStatus


class RootCommand(Command):
    """Root command of your application"""
    name = 'sample'
    # short_description is ignored on root command
    long_description = 'This is a sample command using uroboros'

    def build_option(self, parser):
        """Add optional arguments"""
        parser.add_argument('--version',
                            action='store_true',
                            default=False,
                            help='Print version')
        return parser

    def run(self, args):
        """Your own script to run"""
        if args.version:
            print("{name} v{version}".format(
                name=self.name, version=version))
        else:
            self.print_help()
        return ExitStatus.SUCCESS


class HelloCommand(Command):
    """Sub command of root"""
    name = 'hello'
    short_description = 'Hello world!'
    long_description = 'Print "Hello world!" to stdout'

    def run(self, args):
        print(self.short_description)
        return ExitStatus.SUCCESS


# Create command tree
root_cmd = RootCommand()
root_cmd.add_command(HelloCommand())

if __name__ == '__main__':
    exit(root_cmd.execute())
