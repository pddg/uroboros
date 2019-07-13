from uroboros import Command, ExitStatus

from .envs import get, list_


class EnvCommand(Command):

    name = "env"
    short_description = "Get or set env vars"
    long_description = "Configure environment variables or showing it. " \
                       "This command does not affect your environment. "

    def run(self, args):
        self.print_help()
        return ExitStatus.SUCCESS


command = EnvCommand()
command.add_command(get.command)
command.add_command(list_.command)
