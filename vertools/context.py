import configparser
import engfmt


converters = {
    'Input': {
        'tstart': engfmt.Quantity,
        'tend': engfmt.Quantity,
        'tstep': engfmt.Quantity
    },
    'Simulation': {
        'log': lambda s: True if s.lower() == 'true' else False,
        'tstart': engfmt.Quantity,
        'tend': engfmt.Quantity,
        'tstep': engfmt.Quantity
    },
    'Verification': {
        'log': lambda s: True if s.lower() == 'true' else False,
        'tstart': engfmt.Quantity,
        'tend': engfmt.Quantity,
        'tstep': engfmt.Quantity
    },
}


class Scope:
    """A data container with scoping capabilities
    Attributes:
        data (dict): data
        upper (Scope): more local scope
        lower (Scope): more global scope
    """
    def __init__(self, data=None):
        """Initialize scope
        Args:
            data (dict): data to contain in the Scope
        """
        self.data = data if data is not None else {}
        self.upper = None
        self.lower = None

    @classmethod
    def from_config(cls, filename):
        """Generate a Scope by analysing a config file
        Args:
            filename (str): configuration file name
        Returns:
            Scope
        """
        data = {}
        config = configparser.ConfigParser()
        config.read(filename)
        for section in config:
            data[section] = {}
            for parameter in config[section]:
                converter = converters.get(section, {}).get(parameter, str)
                data[section][parameter] = converter(config[section][parameter])
        return cls(data)

    @classmethod
    def from_cli(cls, args):
        """Generate a Scope from the command line arguments
        Args:
            args (argparse.NameSpace): command line arguments
        Returns:
            Scope
        """
        # Filter away the None
        raise NotImplementedError()

    def get(self, section, parameter, *args, **kwargs):
        """Get a parameter's value
        Args:
            section (str): section name
            parameter (str): parameter name
            *args: arbitrary positional arguments
            **kwargs: arbitrary keyword arguments
        Returns:
            Scope
        """
        if section in self.data:
            if parameter in self.data[section]:
                return self.data[section][parameter]
            else:
                raise Scope.NoParameterError("Parameter not found", parameter)
        else:
            raise Scope.NoSectionError("Section not Found")

    def has_section(self, section):
        """Check if scope contains the requested section
        Args:
            section (str): section name
        Returns:
            bool
        """
        return self.data.has_section(section)

    def __contains__(self, section):
        return section in self.data

    def __getitem__(self, section):
        return self.data[section]

    def __str__(self):
        str(self.data)

    class NoSectionError(configparser.NoSectionError):
        pass

    class NoParameterError(configparser.NoOptionError):
        pass


class Context:
    """A manager for multiple nested scopes
    Attributes:
        _head (Scope): service internal scope
        _tail (Scope): service internal scope
    """
    def __init__(self):
        """Initialize context"""
        # Generate empty guard scopes
        self._head = Scope()
        self._tail = Scope()
        # Set cross references
        self._head.lower = self._tail
        self._tail.upper = self._head

    @staticmethod
    def place_between(scope, first, second):
        """Place a scope in between two already existing scopes
        Args:
            scope (Scope): scope to place
            first (Scope): higher scope (more local)
            second (Scope): lower scope (more global)
        """
        # Insert node
        first.lower = scope
        second.upper = scope
        # Set its connections
        scope.upper = first
        scope.lower = second

    def append_local(self, scope):
        """Append a new local scope
        Args:
            scope (Scope): new scope to append
        """
        self.place_between(scope, self._head, self.most_local())

    def append_global(self, scope):
        """Append a new global scope
        Args:
            scope (Scope): new scope to append
        """
        self.place_between(scope, self.most_global(), self._tail)

    def most_local(self):
        """Get the most local scope in the chain"""
        return self._head.lower

    def most_global(self):
        """Get the most global scope in the chain"""
        return self._tail.upper

    def get(self, section, parameter, *args, **kwargs):
        """Get the value of a parameter
        Args:
            section (str): section name
            parameter (str): parameter name
            *args: arbitrary positional arguments
            **kwargs: arbitrary keyword arguments
        Returns:
            Any
        Raises:
            Context.LookupError: when a section or parameter is not found in any scope
        """
        return self._get(self.most_local(), section, parameter, *args, **kwargs)

    def _get(self, scope, section, parameter, *args, **kwargs):
        """Recursive version for the Context.get method"""
        if section in scope:
            if parameter in scope[section]:
                return scope.get(section, parameter, *args, **kwargs)
        if scope.lower is not self._tail:
            return self._get(scope.lower, section, parameter)
        else:
            raise Context.LookupError(f"Context cannot find parameter {parameter} of section {section} under any scope")

    def __str__(self):
        s = ''
        i = 0
        current_node = self.most_local()
        while current_node != self._tail:
            s += f"Scope {i}: {str(current_node)}\n"
            i+=1
            current_node = current_node.lower
        return s

    class LookupError(LookupError):
        pass
