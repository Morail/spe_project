import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate
import time

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


# Print out the overall stats
def print_tables(data_, log_, save_fig):

    res = []
    # Headers to be printed out
    headers_ = ['protocol', 'num_stations', 'obs', 'mean', 'var', 'std', 'median', 'mad', 'CIs median',
                'gap', 'gini', 'CoV', 'percentiles']

    for d in data_:
        row = []
        for h in headers_:
            row.append(d[h] if h in d else np.nan)
        res.append(row)

    log_.info("Overall statistics for the simulation:\n" + tabulate(res, headers=headers_, tablefmt="grid"))

    if save_fig:

        # Simplest version
        with open('./data/%s-stats.dat' % (time.strftime("%Y%m%d-%H%M")), 'w') as f:
            f.write(tabulate(res, headers=headers_, tablefmt="grid"))

        # Markdown, github style
        with open('./data/%s-stats.md' % (time.strftime("%Y%m%d-%H%M")), 'w') as f:
            f.write(tabulate(res, headers=headers_, tablefmt="github"))

        # LateX
        with open('./data/%s-stats.latex' % (time.strftime("%Y%m%d-%H%M")), 'w') as f:
            f.write(tabulate(res, headers=headers_, tablefmt="latex"))


# Deprecated
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


# Load stats into a Pandas DataFrame
def load_df(stats):
    return pd.DataFrame(stats)
