import vertools
import vertools.cli
import vertools.context


def main():
    """Main function"""
    # Generate context
    context = vertools.context.Context()
    global_config = vertools.context.Scope.from_config(vertools.rootdir/'assets/default.config')
    context.append_local(global_config)
    # Parse command line arguments
    args = vertools.cli.parse()
    if args.local_config is not None:
        local_config = vertools.context.Scope.from_config(args.local_config)
        context.append_local(local_config)
    cl_config = vertools.context.Scope(vertools.cli.Contextualize.SECTIONS)
    context.append_local(cl_config)
    # Call the associated command
    args.func(args, context)


if __name__ == '__main__':
    main()
