from commands import root, version, env


def main():
    root_cmd = root.command
    root_cmd.add_command(
        version.command,
        env.command
    )
    return root_cmd.execute()


if __name__ == '__main__':
    exit(main())
