class ConfigException(Exception):
    
    def __init__(self, message):
        super().__init__(message)


class InvalidFormatException(Exception):
    
    pass
