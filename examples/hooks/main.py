import logging
import sys

import uroboros

logger = logging.getLogger(__name__)


class RootCommand(uroboros.Command):

    name = "hook_feature"
    long_description = "Example of how to use hook"

    def build_option(self, parser):
        parser.add_argument('--version',
                            action='store_true',
                            default=False,
                            help='Print version')
        log = parser.add_argument_group("LOGGING")
        log.add_argument('-v',
                         '--verbose',
                         action='store_true',
                         default=False,
                         help='Enable debug logs')
        return parser

    def before_validate(self, unsafe_args):
        """
        `unsafe_args` is not validated. Use it carefully.
        For example, this method can configure logging configurations.
        See https://github.com/pddg/uroboros/issues/5 for detail.
        """
        root_logger = logging.getLogger()
        if unsafe_args.verbose:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)
        log_fmt = "[%(levelname)s %(asctime)s] %(message)s"
        formatter = logging.Formatter(log_fmt)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)
        logger.debug("`before_validate` of RootCommand is called")
        return unsafe_args

    def after_validate(self, safe_args):
        logger.debug("`after_validate` of RootCommand is called")
        return safe_args

    def run(self, args):
        logger.debug("`run` of RootCommand is called")
        if args.version:
            print("{name} v{version}".format(
                name=self.name, version=uroboros.version))
        else:
            self.print_help()
        return uroboros.ExitStatus.SUCCESS


class HelloCommand(uroboros.Command):

    name = "hello"
    short_description = "Print 'Hello {name}'"
    long_description = "Print 'Hello {name}' except for 'Banana' " \
                       "because I do not like a banana."

    def build_option(self, parser):
        parser.add_argument("name", type=str, help="Name to hello")
        return parser

    def validate(self, args):
        if args.name.lower() == 'banana':
            return [Exception('I hate BANANA :(')]
        return []

    def before_validate(self, unsafe_args):
        logger.debug("`before_validate` of HelloCommand is called")
        return unsafe_args

    def after_validate(self, safe_args):
        """
        You can set new variables to `safe_args` in this method.
        The validation is completed before calling this method.
        So you do not need to validate `safe_args` twice.
        """
        logger.debug("`after_validate` of HelloCommand is called")
        safe_args.message = "Hello " + safe_args.name
        return safe_args

    def run(self, args):
        logger.info(args.message)
        return uroboros.ExitStatus.SUCCESS


root_cmd = RootCommand()
root_cmd.add_command(HelloCommand())


if __name__ == "__main__":
    exit(root_cmd.execute())
