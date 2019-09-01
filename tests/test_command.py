import argparse
import logging
from unittest import mock

import pytest

from uroboros.errors import CommandDuplicateError
from .base import RootCommand, SecondCommand, ThirdCommand


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

    def test_add_others(self):
        root = RootCommand()
        with pytest.raises(AssertionError):
            root.add_command("")

    @pytest.mark.parametrize(
        'command_set', [
            {RootCommand(): {}},
            {RootCommand(): {SecondCommand(): {}}},
            {RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}},
            {RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}},
        ]
    )
    def test_get_all_sub_commands(self, command_set):

        def add_command(cmd, cmd_set):
            for c, sub_set in cmd_set.items():
                cmd.add_command(c)
                add_command(c, sub_set)

        for root, sub_commands in command_set.items():
            add_command(root, sub_commands)

        root = list(command_set.keys())[0]
        assert command_set == root.get_all_sub_commands()

    @pytest.mark.parametrize(
        'command_set,argv', [
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}}, []),
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}}, ['second']),
            ({RootCommand(): {SecondCommand(): {ThirdCommand(): {}}}}, ['second', 'third']),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}}, ['second']),
            ({RootCommand(): {SecondCommand(): {}, ThirdCommand(): {}}}, ['third']),
        ]
    )
    def test_get_sub_commands(self, command_set, argv):

        def add_command(cmd, cmd_set):
            for c, sub_set in cmd_set.items():
                cmd.add_command(c)
                add_command(c, sub_set)

        for root, sub_commands in command_set.items():
            add_command(root, sub_commands)

        root = list(command_set.keys())[0]
        root.initialize()
        args = root._parser.parse_args(argv)
        cmd_names = [cmd.name for cmd in root.get_sub_commands(args)]
        assert argv == cmd_names

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

    def test_before_hook(self):
        args = argparse.Namespace()
        root = RootCommand()
        assert root.before_validate(args) == args

    @pytest.mark.parametrize(
        'commands', [
            [RootCommand()],
            [RootCommand(), SecondCommand()],
            [RootCommand(), SecondCommand(), ThirdCommand()]
        ]
    )
    def test_pre_hook(self, commands):
        root = commands[0]
        args = root._pre_hook(argparse.Namespace(), commands[1:])
        for cmd in commands:
            key = "before_validate_{}".format(cmd.name)
            assert getattr(args, key, None) == cmd.value
