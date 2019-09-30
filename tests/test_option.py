import argparse

import pytest

import uroboros


class SampleOption(uroboros.Option):

    name = 'option'
    value = 'option'

    def build_option(self,
                     parser: 'argparse.ArgumentParser'
                     ) -> 'argparse.ArgumentParser':
        parser.add_argument('--{}'.format(self.name),
                            default=self.value,
                            type=str)
        return parser

    def validate(self,
                 args: 'argparse.Namespace'
                 ) -> 'List[Exception]':
        if getattr(args, self.name) != self.value:
            return [Exception("{} is expected".format(self.value))]
        return []

    def before_validate(self,
                        unsafe_args: 'argparse.Namespace'
                        ) -> 'argparse.Namespace':
        setattr(
            unsafe_args,
            'before_validate_{}'.format(self.name),
            self.value
        )
        return unsafe_args

    def after_validate(self, safe_args):
        setattr(
            safe_args,
            'after_validate_{}'.format(self.name),
            self.value
        )
        return safe_args


class NoHookOption(uroboros.Option):
    name = 'nohook'
    value = 'nohook'

    def build_option(self,
                     parser: 'argparse.ArgumentParser'
                     ) -> 'argparse.ArgumentParser':
        parser.add_argument("--{}".format(self.name), default=self.value)
        return parser


class TestOption(object):

    def test_no_before_validate(self):
        args = argparse.Namespace()
        nohook = NoHookOption()
        assert nohook.before_validate(args) == args

    def test_before_hook(self):
        args = argparse.Namespace()
        opt = SampleOption()
        hooked_args = opt.after_validate(args)
        actual = getattr(
            hooked_args, "after_validate_{}".format(opt.name))
        assert actual == opt.value

    def test_no_after_validate(self):
        args = argparse.Namespace()
        nohook = NoHookOption()
        assert nohook.before_validate(args) == args

    def test_after_hook(self):
        args = argparse.Namespace()
        opt = SampleOption()
        hooked_args = opt.after_validate(args)
        actual = getattr(
            hooked_args, "after_validate_{}".format(opt.name))
        assert actual == opt.value

    def test_cannot_instantiate(self):
        class Opt(uroboros.Option):
            pass
        with pytest.raises(TypeError):
            Opt()

    @pytest.mark.parametrize(
        "option", [
            NoHookOption(),
            SampleOption(),
        ]
    )
    def test_call_twice(self, option):
        expected = option.get_parser()
        assert option.get_parser() == expected

