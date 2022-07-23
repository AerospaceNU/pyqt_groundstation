import configparser

config = configparser.ConfigParser()
config.read("config.ini")


def format_key(key: str):
    return key.replace(" ", "_")


class ConfigSaver:
    @staticmethod
    def save(section: str, key: str, data: str):
        key = format_key(key)
        if section not in config:
            config[section] = {}

        config[section][key] = str(data)

        with open("config.ini", "w") as configfile:
            config.write(configfile)

    @staticmethod
    def setDefault(section: str, key: str, data: str):
        key = format_key(key)
        if section not in config:
            config[section] = {}

        if key not in config[section]:
            config[section][key] = str(data)

            with open("config.ini", "w") as configfile:
                config.write(configfile)

    @staticmethod
    def get(section: str, key: str, default=None):
        key = format_key(key)
        if section not in config:
            if default is None:
                return None
            else:
                config[section] = {}

        # Default set but section may or may not exist

        if key not in config[section]:
            if default is not None:
                ConfigSaver.save(section, key, default)
                return default
            else:
                return None

        return config[section][key]


# ConfigSaver.save("f", "o", "3")
# print(ConfigSaver.get("foo","bar"))
# print(type(ConfigSaver.get("foo","bar")))
