import uroboros


def print_version():
    print("multiple modules example v{version}"
          .format(version=uroboros.version))


class RootCommand(uroboros.Command):

    name = 'multi_module'
    long_description = 'Sample of uroboros. ' \
                       'Use multiple modules to make this app'

    def build_option(self, parser):
        parser.add_argument('--version',
                            action='store_true',
                            default=False,
                            help='Print version')
        return parser

    def run(self, args):
        if args.version:
            print_version()
        else:
            self.print_help()
        return uroboros.ExitStatus.SUCCESS


root_cmd = RootCommand()
