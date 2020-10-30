import os

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
    # Check for a local config
    if args.local_config is not None:
        local_config = vertools.context.Scope.from_config(args.local_config)
        context.append_local(local_config)
    else:
        # Try to look for default "vertools.config" file
        if 'vertools.config' in os.listdir(os.getcwd()):
            local_config = vertools.context.Scope.from_config('vertools.config')
            context.append_local(local_config)
    # Push command line arguments into context
    cl_config = vertools.context.Scope(vertools.cli.Contextualize.SECTIONS)
    context.append_local(cl_config)
    # Call the requested command's associated function
    args.func(args, context)()


if __name__ == '__main__':
    main()
