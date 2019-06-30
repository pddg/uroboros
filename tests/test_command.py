import argparse
import logging
from unittest import mock

import pytest

import uroboros
from uroboros.errors import CommandDuplicateError


class RootCommand(uroboros.Command):
    name = 'root'
    description = 'command of root'

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
    description = 'command of second'

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
    description = 'command of third'

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


@pytest.fixture
def commands():
    return RootCommand(), SecondCommand(), ThirdCommand()


def get_sub_commands(cmd_set):
    if len(cmd_set) == 0:
        return []
    cmds = []
    for c, sub_set in cmd_set.items():
        cmds.append(c)
        c.sub_commands = get_sub_commands(sub_set)
    return cmds


class TestCommand(object):

    @pytest.mark.parametrize(
        'command', [
            RootCommand(),
            SecondCommand(),
            ThirdCommand()
        ]
    )
    def test_build_option(self, command):
        parser = argparse.ArgumentParser()
        parser = command.build_option(parser)
        expected = command.value
        actual = parser.get_default(command.name)
        assert expected == actual

    @pytest.mark.parametrize(
        'command', [
            RootCommand(),
            SecondCommand(),
            ThirdCommand()
        ]
    )
    def test_validate(self, command):
        valid_args = mock.MagicMock(
            **{command.name: command.value}
        )
        expected = []
        actual = command.validate(valid_args)
        assert expected == actual
        invalid_args = mock.MagicMock(
            **{command.name: None}
        )
        expected = [command.error]
        actual = command.validate(invalid_args)
        assert expected == actual

    @pytest.mark.parametrize(
        'command_set', [
            {RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
            {RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
            {RootCommand(): {}, SecondCommand(): {}, ThirdCommand(): {}}
        ]
    )
    def test_increment_nest(self, command_set):
        result_set = {}

        def count_nest(cmd_set, count):
            count += 1
            for c, sub_set in cmd_set.items():
                result_set[c] = count
                count_nest(sub_set, count)

        for root, sub_commands in command_set.items():
            root.sub_commands = get_sub_commands(sub_commands)
            root.increment_nest(-1)
        layer_num = -1
        count_nest(command_set, layer_num)
        for cmd, expected in result_set.items():
            actual = cmd._layer
            assert expected == actual

    @pytest.mark.parametrize(
        'command_set', [
            {RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
            {RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
            {RootCommand(): {}, SecondCommand(): {}, ThirdCommand(): {}}
        ]
    )
    def test_register_parent(self, command_set):
        result_set = {}

        def collect_ids(parent_ids, cmd_set):
            for c, sub_set in cmd_set.items():
                current_set = parent_ids | {id(c)}
                result_set[c] = current_set
                collect_ids(current_set, sub_set)

        for root, sub_commands in command_set.items():
            root.sub_commands = get_sub_commands(sub_commands)
            root.register_parent(set())
        collect_ids(set(), command_set)

        for cmd, expected in result_set.items():
            actual = cmd._parent_ids
            assert expected == actual

    @pytest.mark.parametrize(
        'command_set', [
            {RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
            {RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
            {RootCommand(): {}, SecondCommand(): {}, ThirdCommand(): {}}
        ]
    )
    def test_add_command(self, command_set):
        result_set = {}

        def add_command(cmd, cmd_set):
            result_set[cmd] = set()
            for c, sub_set in cmd_set.items():
                result_set[cmd].add(id(c))
                cmd.add_command(c)
                add_command(c, sub_set)

        for root, sub_commands in command_set.items():
            add_command(root, sub_commands)

        for command, expected in result_set.items():
            actual = command._sub_command_ids
            assert actual == expected

    @pytest.mark.parametrize(
        'command_set', [
            {RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
            {RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
        ]
    )
    def test_add_duplicate_command(self, command_set):
        result_set = {}

        def add_command(parent_cmds, cmd, cmd_set):
            result_set[cmd] = parent_cmds + [cmd]
            for c, sub_set in cmd_set.items():
                cmd.add_command(c)
                add_command(result_set[cmd], c, sub_set)

        for root, sub_commands in command_set.items():
            add_command([], root, sub_commands)

        for command, parents in result_set.items():
            for parent in parents:
                with pytest.raises(CommandDuplicateError):
                    command.add_command(parent)

    @pytest.mark.parametrize(
        'command_set,argv,expected', [
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
             "root second third", ThirdCommand.value),
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
             "root second", SecondCommand.value),
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
             "root", RootCommand.value),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
             "root second", SecondCommand.value),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
             "root third", ThirdCommand.value),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
             "root", RootCommand.value),
        ]
    )
    def test_execute(self, command_set, argv, expected, capsys):

        def add_command(cmd, cmd_set):
            for c, sub_set in cmd_set.items():
                cmd.add_command(c)
                add_command(c, sub_set)

        for root, sub_commands in command_set.items():
            add_command(root, sub_commands)
            root.execute(argv.split(' ')[1:])
            stdout = capsys.readouterr()
            actual = stdout.out.splitlines()[0]
            assert actual == str(expected)

    @pytest.mark.parametrize(
        'command_set,argv,expected', [
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
             "root second third --third invalid", "third"),
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
             "root second --second 10", "second"),
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
             "root --root", "root"),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
             "root second --second 10", "second"),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
             "root third --third invalid", "third"),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
             "root --root", "root"),
        ]
    )
    def test_violates_validation_argv(
            self, command_set, argv, expected, caplog):

        def add_command(cmd, cmd_set):
            for c, sub_set in cmd_set.items():
                cmd.add_command(c)
                add_command(c, sub_set)

        for root, sub_commands in command_set.items():
            add_command(root, sub_commands)
            root.execute(argv.split(' ')[1:])
            out = caplog.record_tuples[0]
            actual = out[1:]
            assert actual == (logging.ERROR, expected)
