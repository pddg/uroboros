def get_args_command_name(layer: int):
    return "__layer{layer}_command".format(layer=layer)


def get_args_validator_name(layer: int):
    return "__layer{layer}_validator".format(layer=layer)


def get_args_section_name(layer: int):
    return "__layer{layer}_parser".format(layer=layer)


def call_one_by_one(objs, method_name: str, args, **kwargs):
    for obj in objs:
        assert hasattr(obj, method_name), \
            "'{cmd}' has no method '{method}".format(
                cmd=obj.__name__,
                method=method_name
            )
        args = getattr(obj, method_name)(args, **kwargs)
    return args
