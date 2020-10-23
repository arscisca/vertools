import vertools
import vertools.cli
import vertools.context


def main():
    """Main function"""
    # Read configuration files
    base_context = vertools.context.Context.from_config(vertools.rootdir/'assets/default.config')
    # Parse command line arguments
    args = vertools.cli.parse()
    # Call the associated command
    args.func(base_context, **vars(args))


if __name__ == '__main__':
    main()
