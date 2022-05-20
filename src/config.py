import configparser

config = configparser.ConfigParser()
config.read("config.ini")


class ConfigSaver:
    @staticmethod
    def save(section: str, key: str, data: str):
        if section not in config:
            config[section] = {}

        config[section][key] = str(data)

        with open("config.ini", "w") as configfile:
            config.write(configfile)

    @staticmethod
    def get(section: str, key: str):
        if section not in config:
            return None

        if key not in config[section]:
            return None

        return config[section][key]


# ConfigSaver.save("f", "o", "3")
# print(ConfigSaver.get("foo","bar"))
# print(type(ConfigSaver.get("foo","bar")))
