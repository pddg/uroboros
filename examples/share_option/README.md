# Example of sharing options among some commands

```bash
$ python main.py -h
usage: share_option [-h] [--version] {dirs,files} ...

Example of using Option

optional arguments:
  -h, --help    show this help message and exit
  --version     Print version

Sub commands:
  {dirs,files}
    dirs        Show directories
    files       Show files
$ python main.py dirs -h
usage: share_option dirs [-h] [-a] path

Show directories in given path

positional arguments:
  path            Path to show

optional arguments:
  -h, --help      show this help message and exit
  -a, --absolute  Show absolute path
$ python main.py dirs ../
../share_option
../simple
../multiple_modules
$ python main.py files -h
usage: share_option files [-h] [-a] [-e [EXTENSION [EXTENSION ...]]] path

Show files in given path

positional arguments:
  path                  Path to show

optional arguments:
  -h, --help            show this help message and exit
  -a, --absolute        Show absolute path
  -e [EXTENSION [EXTENSION ...]], --exclude [EXTENSION [EXTENSION ...]]
                        File extension to hide
$ python main.py files ./ -e py
README.md
```

## License

This example is licensed under [Apache 2.0](../../LICENSE).
