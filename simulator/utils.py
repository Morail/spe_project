import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate

from station import Station


def init_logger(logger_type='custom_logger', time_format="%Y-%m-%d %H:%M:%S", is_debug=False):
    # Create a custom formatter with your desired time format
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt=time_format)
    # Create a logger and set the custom formatter
    logger = logging.getLogger(logger_type)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set the log level (optional, can be DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG if is_debug else logging.INFO)

    return logger


# Init stations
def init_stations(num_, packet_probs, packet_sizes, rng_, max_backoff_time):
    # Create a new Station by passing:
    # - param i to be used as unique identifier for the station
    # - the probability for the given Station to generate a packet to transmit for each frame
    # - the packet size
    stations = [Station(i, packet_probs[i], packet_sizes[i], rng_, max_backoff_time) for i in range(num_)]

    return stations


def print_tables(stats_, metric):

    data_ = []
    headers_ = ['protocol', '# stations', 'avg '+metric , 'std '+metric]

    for ns, vns in stats_.items():
        for p, vp in vns.items():
            value = vp[metric]
            mean = np.mean(value)
            std = np.std(value)
            data_.append([p, ns, mean, std])

    return tabulate(data_, headers=headers_)


def plot_stats(stats, num_stations):
    metrics = ['throughput', 'collision_rate', 'delay', 'retransmissions']
    protocols = ['aloha', 'csma']

    for metric in metrics:
        plt.figure(figsize=(14, 7))

        for protocol in protocols:
            try:
                means = [np.mean(stats[ns][protocol][metric]) for ns in num_stations]
                stds = [np.std(stats[ns][protocol][metric]) for ns in num_stations]
            except Exception as e:
                print(e)
                continue

            plt.errorbar(num_stations, means, yerr=stds, label=protocol.upper(), capsize=5, fmt='o-', elinewidth=2,
                         markeredgewidth=2)

        plt.title(f'Comparison of {metric.capitalize()} between ALOHA and CSMA')
        plt.xlabel('Number of Nodes')
        plt.ylabel(metric.capitalize())
        plt.legend()
        plt.grid(True)
        plt.show()


def load_df(stats):
    return pd.DataFrame(stats)
