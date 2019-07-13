# uroboros

[![Build Status](https://travis-ci.com/pddg/uroboros.svg?branch=master)](https://travis-ci.com/pddg/uroboros) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/uroboros.svg)](https://pypi.python.org/pypi/uroboros/) [![PyPI version shields.io](https://img.shields.io/pypi/v/uroboros.svg)](https://pypi.python.org/pypi/uroboros/)
 [![GitHub license](https://img.shields.io/github/license/pddg/uroboros.svg)](https://github.com/pddg/uroboros/blob/master/LICENSE)



Simple framework for building scalable CLI tool.

**NOTE**  
This framework currently under development. Please be careful to use.

## Features

- Simple interface
- Pure python
    - Thin wrapper of `argparse`
    - No third party dependencies
- Easy to reuse common options
- Easy to create sub commands
    - Nested sub command is also supported

## Environment

- Python >= 3.5
    - No support for python 2.x

Install uroboros

```bash
$ pip install uroboros
```

## How to use

Implement your command using `uroboros.Command` and create a command tree.

```python
# sample.py
from uroboros import Command
from uroboros.constants import ExitStatus

class RootCommand(Command):
    """Root command of your application"""
    name = 'sample'
    long_description = 'This is a sample command using uroboros'

    def build_option(self, parser):
        """Add optional arguments"""
        parser.add_argument('--version', action='store_true', default=False, help='Print version')
        return parser

    def run(self, args):
        """Your own script to run"""
        if args.version:
            print("{name} v{version}".format(
                name=self.name, version='1.0.0'))
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
```

Then, your command works completely.

```bash
$ python sample.py -h
usage: sample [-h] [--version] {hello} ...

This is a sample command using uroboros

optional arguments:
  -h, --help  show this help message and exit
  --version   Print version

Sub commands:
  {hello}
    hello     Hello world!
$ python sample.py --version
sample v1.0.0
$ python sample.py hello
Hello world!
```

If you want to use new sub command `sample.py hello xxxx`, you just implement new `XXXXCommand` and add it to `Hello`.

```python
root_cmd = RootCommand().add_command(
    HelloCommand().add_command(
        XXXXCommand()
    )
)
```

You can see other examples in [examples](examples).

## Develop

First, clone this repository and install uroboros with editable option.

```bash
$ git clone https://github.com/pddg/uroboros
$ cd /path/to/uroboros
$ pip install -e .
```

Use `Pipenv` for lint and test.

```bash
# Create environment
$ pipenv install --dev
# Execute lint by flake8
$ pipenv run lint
# Execute test by py.test
$ pipenv run test
```

Also support test with `tox`. Before execute test with `tox`, you should make available to use python `3.5` and `3.6`, `3.7`.

## License

Apache 2.0

## Author

Shoma Kokuryo
