import configparser

config = configparser.ConfigParser()
config.read("config.ini")


def format_key(key: str):
    return key.replace(" ", "_")


class ConfigSaver:
    def __init__(self, section: str):
        self.section = section

    def getSections(self):
        return config.sections()

    def save(self, key: str, data: str):
        key = format_key(key)
        if self.section not in config:
            config[self.section] = {}

        config[self.section][key] = str(data)

        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def setDefault(self, key: str, data: str):
        key = format_key(key)
        if self.section not in config:
            config[self.section] = {}

        if key not in config[self.section]:
            config[self.section][key] = str(data)

            with open("config.ini", "w") as configfile:
                config.write(configfile)

    def get(self, key: str, default=None, type=str):
        key = format_key(key)
        if self.section not in config:
            if default is None:
                return None
            else:
                config[self.section] = {}

        # Default set but section may or may not exist
        if key not in config[self.section]:
            if default is not None:
                self.save(key, default)
                return default
            else:
                return None

        string_ret = config[self.section][key]
        return type(string_ret)
