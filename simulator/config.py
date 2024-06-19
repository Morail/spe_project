import configparser


class Config:
    """
    Reads simulation config from configuration file and store into its instance variables.
    The configuration file is in ini format with the addition of text comments
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
        self.list_num_stations = [int(ns) for ns in config[section]['NumStations'].strip().split(',')]
        self.seed = config.get(section, 'Seed').strip()
        self.is_debug = config.getboolean(section,'IsDebug')

