FORMAT_CODES = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}


def decorate(string, codes):
    """Surround a string with ANSI escape sequences to color outputs.
    Args:
        string (str): string to be decorated
        codes (list(str)): a list of format codes or ANSI formatting characters
    Returns:
        str
    """
    result = ''
    for code in codes:
        code = FORMAT_CODES[code] if code in FORMAT_CODES else code
        result += code
    result += string + FORMAT_CODES['ENDC'] * len(codes)
    return result


def indent(message, indentation):
    """Indent a string with spaces.
    Args:
        message (str): string to be indented
        indentation (int): indentation level
    Returns:
        str
    """
    return ' ' * indentation + message


def print_message(message, style, indentation, title='', title_style=None):
    """Print a fully fledged message
    Args:
        message (str): message to print
        style (list): list of format codes or ANSI formatting characters
        indentation (int): indentation level
        title (str): title to print before the message, as in "title: message"
        title_style (list): list of format codes or ANSI formatting characters to apply to the title only
    """
    output = ''
    if title:
        if title_style is None:
            title_style = style
        output += decorate(title + ': ', title_style)
    output += decorate(message, style)
    output = indent(output, indentation)
    print(output)


def update(message, indentation=0):
    """Print a simple unformatted update
        Args:
            message (str): error message
            indentation (int): output indentation level
    """
    print_message(message, [], indentation)


def error(message, indentation=0):
    """Print an error message
    Args:
        message (str): error message
        indentation (int): output indentation level
    """
    print_message(message, ['FAIL'], indentation, 'ERROR', ['FAIL', 'BOLD'])


def warning(message, indentation=0):
    """Print a warning message.
    Args:
        message (str): warning message
        indentation (int): indentation level
    """
    print_message(message, ['WARNING'], indentation, 'WARNING', ['WARNING', 'BOLD'])


def status(message, indentation=0):
    """Print a status message.
       Args:
           message (str): status message
           indentation (int): indentation level
    """
    print_message(message, ['BLUE'], indentation)


def success(message, indentation=0):
    """Print a success message.
       Args:
           message (str): success message
           indentation (int): indentation level
    """
    print_message(message, ['GREEN'], indentation)


def confirm(message, default=True):
    """Ask user to confirm action.
    Args:
        message (str): prompt message
        default (bool): default answer if the user only presses ENTER
    Returns:
        bool
    """
    pattern = 'Y/n' if default is True else 'y/N'
    valid = False
    while not valid:
        answer = input(f"{message} [{pattern}]").lower()
        if answer == '':
            return default
        elif answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            print("Invalid answer")
