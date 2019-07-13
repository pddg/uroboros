import os

from uroboros import Command, ExitStatus


class GetCommand(Command):

    name = "get"
    short_description = "Show value"
    long_description = "Show value of given env var"

    def build_option(self, parser):
        parser.add_argument('name', type=str, help='Env var name')
        parser.add_argument('-u', '--upper', default=False, action='store_true',
                            help='Capitalize all chars of given name')
        return parser

    def run(self, args):
        key = args.name
        if args.upper:
            key = key.upper()
        var = os.getenv(key)
        if var is None:
            print("Specified variable does not exists: '{}'".format(key))
            return ExitStatus.FAILURE
        print("{}={}".format(key, var))
        return ExitStatus.SUCCESS


command = GetCommand()
