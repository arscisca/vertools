import os
import subprocess


def remove_files(*files):
    """Delete files from the disk.
    Args:
        files (str): list of paths to files to erase. If a file does not exist, it is simply skipped.
    """
    for file in files:
        try:
            os.remove(file)
        except OSError:
            pass


def exists(path):
    """Check if path exists
    Args:
        path (str): path
    Returns:
        bool
    """
    return os.path.exists(path)


def is_file(path):
    """Check if a file exists
    Args:
        path (str): path to the file
    Returns:
        bool: True if file exists, False otherwise
    """
    return os.path.isfile(path)


def is_executable(path):
    """Check if a file exists and is executable
    Args:
        path (str): path to the file
    Returns:
        bool: True if file exists and is executable, False otherwise
    """
    return is_file(path) and os.access(path, os.X_OK)


def run_bash(commands, **kwargs):
    """Run a bash command
    Args:
        commands (Union[str, List[str]]): command (or list of commands) to be executed in the same shell
        **kwargs: arbitrary keyword arguments
    Returns:
       subprocess.CompletedProcess
    """
    stdout = kwargs.get('stdout', None)
    stderr = kwargs.get('stderr', None)
    if stdout is False:
        stdout = subprocess.DEVNULL
    if stderr is False:
        stderr = subprocess.DEVNULL
    if isinstance(commands, list):
        command = ' && '.join(commands)
    else:
        command = commands
    status = subprocess.run(command, shell=True, stdout=stdout, stderr=stderr)
    return status


def launch(script, **kwargs):
    """Launch a script
    Args:
        script (str): script path
        **kwargs: arbitrary keyword arguments
    Returns:
        subprocess.CompletedProcess
    """
    #TODO Specific implementation for scripts instead of running a generic command
    return run_bash(script, **kwargs)