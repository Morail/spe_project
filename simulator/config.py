import configparser


class Config:
    """
    Reads simulation config from configuration file. The configuration file is
    in ini format with the addition of text comments
    """

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        section = config['DEFAULT']['env']

        if not section or section == '':
            section = 'DEFAULT'

        self.num_runs = int(config[section]['NumRuns'])
        self.num_epochs = int(config[section]['NumEpochs'])
        self.max_backoff_time = int(config[section]['MaxBackoffTime'])
        self.num_stations = [int(ns) for ns in config[section]['NumStations'].split(',')]
        self.seed = config.get(section, 'Seed')
        self.is_debug = config.getboolean(section,'IsDebug')

