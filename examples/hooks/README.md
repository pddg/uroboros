# Simple example of hook feature

```bash
$ python main.py -h
usage: hook_feature [-h] [--version] [-v] {hello} ...

Example of how to use hook

optional arguments:
  -h, --help     show this help message and exit
  --version      Print version

LOGGING:
  -v, --verbose  Enable debug logs

Sub commands:
  {hello}
    hello        Print 'Hello {name}'
# Print `Hello Mike`
$ python main.py hello Mike
[INFO 2019-09-02 00:17:03,931] Hello Mike
# `Banana` violates the validation
$ python main.py hello Banana
[ERROR 2019-09-02 00:17:24,715] I hate BANANA :(
# Use `--verbose` to change verbosity
$ python main.py --verbose hello Mike
[DEBUG 2019-09-02 00:28:20,358] `before_validate` of RootCommand is called
[DEBUG 2019-09-02 00:28:20,358] `before_validate` of HelloCommand is called
[DEBUG 2019-09-02 00:28:20,358] `after_validate` of RootCommand is called
[DEBUG 2019-09-02 00:28:20,358] `after_validate` of HelloCommand is called
[INFO 2019-09-02 00:28:20,358] Hello Mike
# `after_validate` is not called when the validation returns some exceptions.
$ python main.py --verbose hello Banana
[DEBUG 2019-09-02 00:28:14,125] `before_validate` of RootCommand is called
[DEBUG 2019-09-02 00:28:14,125] `before_validate` of HelloCommand is called
[ERROR 2019-09-02 00:28:14,125] I hate BANANA :(
```

## License

This example is licensed under [Apache 2.0](../../LICENSE).
