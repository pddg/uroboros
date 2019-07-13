import os
from uroboros import Command, ExitStatus


class ListCommand(Command):

    name = 'list'
    short_description = 'Show all vars'
    long_description = 'Show all environment variables in your environment'

    def build_option(self, parser):
        parser.add_argument("-k", "--key-only", default=False,
                            action='store_true', help="Show name only")
        return parser

    def run(self, args):
        env_vars = os.environ
        if args.key_only:
            for key in env_vars.keys():
                print(key)
        else:
            for key, val in env_vars.items():
                print("{}={}".format(key, val))
        return ExitStatus.SUCCESS


command = ListCommand()
