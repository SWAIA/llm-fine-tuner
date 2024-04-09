class BasicInit:
    def __init__(self, configuration=None):
        self.configuration = self._loadConfiguration(configuration)

    # Private method to load and merge configurations
    def _loadConfiguration(self, configuration):
        defaultConfig = self._getDefaultConfig()
        userConfig = configuration if configuration is not None else {}
        return {**defaultConfig, **userConfig}

    # Private method to encapsulate default configuration logic
    def _getDefaultConfig(self):
        try:
            with open('config.json', 'r') as configFile:
                return json.load(configFile)
        except FileNotFoundError:
            print("Default configuration file not found. Using empty configuration.")
            return {}

    # Public method to access the configuration
    def getConfiguration(self):
        return self.configuration