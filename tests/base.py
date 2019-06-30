import uroboros


class RootCommand(uroboros.Command):
    name = 'root'
    long_description = 'command of root'

    error = Exception(name)
    value = False

    def build_option(self, parser):
        parser.add_argument(
            '--{}'.format(self.name), action='store_true',
            default=self.value, help='root argument'
        )
        return parser

    def run(self, args):
        print(args.root)
        return 0

    def validate(self, args):
        if args.root != self.value:
            return [self.error]
        return []


class SecondCommand(uroboros.Command):
    name = 'second'
    long_description = 'command of second'

    error = Exception(name)
    value = 0

    def build_option(self, parser):
        parser.add_argument(
            '--{}'.format(self.name), type=int,
            default=self.value, help='second argument'
        )
        return parser

    def run(self, args):
        print(args.second)
        return 0

    def validate(self, args):
        if args.second != self.value:
            return [self.error]
        return []


class ThirdCommand(uroboros.Command):
    name = 'third'
    long_description = 'command of third'

    error = Exception(name)
    value = 'third'

    def build_option(self, parser):
        parser.add_argument(
            '--{}'.format(self.name), type=str,
            default=self.value, help='third argument'
        )
        return parser

    def run(self, args):
        print(args.third)
        return 0

    def validate(self, args):
        if args.third != self.value:
            return [self.error]
        return []
