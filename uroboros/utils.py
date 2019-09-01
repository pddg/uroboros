def get_args_command_name(layer: int):
    return "__layer{layer}_command".format(layer=layer)


def get_args_validator_name(layer: int):
    return "__layer{layer}_validator".format(layer=layer)


def get_args_section_name(layer: int):
    return "__layer{layer}_parser".format(layer=layer)
