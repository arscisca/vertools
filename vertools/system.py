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


def is_file(path):
    """Check if a fil exists
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


def run_bash(command, **kwargs):
    """Run a bash command
    Args:
        command (str): command to be executed
        **kwargs: arbitrary keyword arguments
    Returns:
       subprocess.CompletedProcess
    """
    stdout = kwargs.get('stdout', None)
    stderr = kwargs.get('stderr', None)
    status = subprocess.run(command, shell=True, stdout=stdout, stderr=stderr)
    return status