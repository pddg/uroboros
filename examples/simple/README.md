# Simple example of using uroboros

You should install `uroboros` before executing examples.

```bash
$ python main.py -h
usage: sample [-h] [--version] {hello} ...

This is a sample command using uroboros

optional arguments:
  -h, --help  show this help message and exit
  --version   Print version

Sub commands:
  {hello}
    hello     Hello world!
$ python main.py --version
sample v0.1.0
$ python main.py hello -h
usage: sample hello [-h]

Print "Hello world!" to stdout

optional arguments:
  -h, --help  show this help message and exit
$ python main.py hello
Hello world!
```

## License

This example is licensed under [Apache 2.0](../../LICENSE).
