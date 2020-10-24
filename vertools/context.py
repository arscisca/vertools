import configparser


class Scope:
    """Scope
    Attributes:
        data (configparser.ConfigParser): data
        upper (Scope): more local scope
        lower (Scope): more global scope
    """
    def __init__(self, data=None):
        self.data = data
        self.upper = None
        self.lower = None

    @classmethod
    def from_config(cls, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        return cls(config)

    @classmethod
    def from_dict(cls, dictionary):
        config = configparser.ConfigParser()
        config.read_dict(dictionary)
        return cls(config)

    def get(self, section, parameter, *args, **kwargs):
        if self.data.has_section(section):
            if parameter in self.data[section]:
                return self.data.get(section, parameter, *args, **kwargs)
            else:
                raise Scope.NoParameterError("Parameter not found", parameter)
        else:
            raise Scope.NoSectionError("Section not Found")

    def has_section(self, section):
        return self.data.has_section(section)

    def __contains__(self, section):
        return section in self.data

    def __getitem__(self, section):
        return self.data[section]

    class NoSectionError(configparser.NoSectionError):
        pass

    class NoParameterError(configparser.NoOptionError):
        pass


class Context:
    def __init__(self):
        # Generate empty guard scopes
        self._head = Scope()
        self._tail = Scope()
        # Set cross references
        self._head.lower = self._tail
        self._tail.upper = self._head

    def place_between(self, scope, first, second):
        # Insert node
        first.lower = scope
        second.upper = scope
        # Set its connections
        scope.upper = first
        scope.lower = second

    def append_local(self, scope):
        self.place_between(scope, self._head, self.most_local())

    def append_global(self, scope):
        self.place_between(scope, self.most_global(), self._tail)

    def most_local(self):
        return self._head.lower

    def most_global(self):
        return self._tail.upper

    def get(self, section, parameter, *args, **kwargs):
        return self._get(self.most_local(), section, parameter, *args, **kwargs)

    def _get(self, scope, section, parameter, *args, **kwargs):
        if section in scope:
            if parameter in scope[section]:
                return scope.get(section, parameter, *args, **kwargs)
        if scope.lower is not self._tail:
            return self._get(scope.lower, section, parameter)
        else:
            raise Context.LookupError(f"Context cannot find parameter {parameter} of section {section} under any scope")

    class LookupError(LookupError):
        pass
