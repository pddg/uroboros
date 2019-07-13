# Example of using multiple modules

Implement commands in some module separately.

```bash
$ python main.py -h
usage: multi_module [-h] [--version] {version,env} ...

Sample of uroboros. Use multiple modules to make this app

optional arguments:
  -h, --help     show this help message and exit
  --version      Print version

Sub commands:
  {version,env}
    version      Print version
    env          Get or set env vars
# Both of `--version` option and `version` command show the version
$ python main.py --version  # or use 'version'
multiple modules example v0.1.0
$ python main.py env -h
usage: multi_module env [-h] {get,list} ...

Configure environment variables or showing it. This command does not affect
your environment.

optional arguments:
  -h, --help  show this help message and exit

Sub commands:
  {get,list}
    get       Show value
    list      Show all vars
$ python main.py env get -h
usage: multi_module env get [-h] [-u] name

Show value of given env var

positional arguments:
  name         Env var name

optional arguments:
  -h, --help   show this help message and exit
  -u, --upper  Capitalize all chars of given name
$ python main.py env get SHELL
SHELL=/bin/bash
```

## License

This example is licensed under [Apache 2.0](../../LICENSE).
