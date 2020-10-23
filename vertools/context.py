import configparser


class Context:
    """Context manager"""
    def __init__(self, data=None):
        self.parent = None
        self.subcontext = None
        self.data = data

    def top_level(self):
        if self.parent is not None:
            return self.parent.top_level()
        else:
            return self

    def bottom_level(self):
        if self.subcontext is not None:
            return self.subcontext.bottom_level()
        else:
            return self

    def override(self, context):
        self.subcontext = context
        context.parent = self

    def get(self, section, attribute):
        if section in self.data:
            if attribute in self.data[section]:
                return self.data[section][attribute]
        if self.subcontext is not None:
            return self.subcontext.get(section, attribute)
        raise Context.ContextError(f"Section {section} or attribute {attribute} does not exist")

    @classmethod
    def from_config(cls, file):
        config = configparser.ConfigParser()
        config.read(file)
        return cls(config)

    class ContextError(LookupError):
        pass
