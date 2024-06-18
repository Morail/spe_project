import configparser
import logging
from station import Station
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate


def init(fn_):
    config = configparser.ConfigParser()
    config.read(fn_)

    num_runs = int(config['DEFAULT']['NumRuns'])
    num_epochs = int(config['DEFAULT']['NumEpochs'])
    max_backoff_time = int(config['DEFAULT']['MaxBackoffTime'])
    num_stations = [int(ns) for ns in config['DEFAULT']['NumStations'].split(',')]
    seed = config['DEFAULT']['Seed']

    return num_runs, num_epochs, num_stations, max_backoff_time, seed


# Init stations
def init_stations(num_, packet_probs, packet_sizes, max_backoff_time):
    # Create a new Station by passing:
    # - param i to be used as unique identifier for the station
    # - the probability for the given Station to generate a packet to transmit for each frame
    # - the packet size
    stations = [Station(i, packet_probs[i], packet_sizes[i], max_backoff_time) for i in range(num_)]

    return stations


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


# First version, deprecated
def old_plot_stats(aloha_throughputs, csma_throughputs, aloha_collision_rates, csma_collision_rates):
    # Plot histogram
    plt.figure(figsize=(14, 7))
    plt.subplot(1, 2, 1)
    plt.hist(aloha_throughputs, bins=50, alpha=0.7, label='ALOHA')
    plt.hist(csma_throughputs, bins=50, alpha=0.7, label='CSMA')
    plt.title('Throughput Distribution')
    plt.xlabel('Throughput')
    plt.ylabel('Frequency')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.hist(aloha_collision_rates, bins=50, alpha=0.7, label='ALOHA')
    plt.hist(csma_collision_rates, bins=50, alpha=0.7, label='CSMA')
    plt.title('Collision Rate Distribution')
    plt.xlabel('Collision Rate')
    plt.ylabel('Frequency')
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Plot bar plot with error bars
    means = [np.mean(aloha_throughputs), np.mean(csma_throughputs)]
    stds = [np.std(aloha_throughputs), np.std(csma_throughputs)]

    plt.figure(figsize=(10, 5))
    plt.bar(['ALOHA', 'CSMA'], means, yerr=stds, alpha=0.7, capsize=10)
    plt.title('Average Throughput with Error Bars')
    plt.xlabel('Protocol')
    plt.ylabel('Throughput')
    plt.show()

    means = [np.mean(aloha_collision_rates), np.mean(csma_collision_rates)]
    stds = [np.std(aloha_collision_rates), np.std(csma_collision_rates)]

    plt.figure(figsize=(10, 5))
    plt.bar(['ALOHA', 'CSMA'], means, yerr=stds, alpha=0.7, capsize=10)
    plt.title('Average Collision Rate with Error Bars')
    plt.xlabel('Protocol')
    plt.ylabel('Collision Rate')
    plt.show()

    # Plot error bars only
    x = np.array([1, 2])
    throughputs_means = [np.mean(aloha_throughputs), np.mean(csma_throughputs)]
    throughputs_stds = [np.std(aloha_throughputs), np.std(csma_throughputs)]

    plt.figure(figsize=(10, 5))
    plt.errorbar(x, throughputs_means, yerr=throughputs_stds, fmt='o', capsize=5, elinewidth=2, markeredgewidth=2)
    plt.xticks(x, ['ALOHA', 'CSMA'])
    plt.title('Throughput with Error Bars')
    plt.xlabel('Protocol')
    plt.ylabel('Throughput')
    plt.show()

    collision_rates_means = [np.mean(aloha_collision_rates), np.mean(csma_collision_rates)]
    collision_rates_stds = [np.std(aloha_collision_rates), np.std(csma_collision_rates)]

    plt.figure(figsize=(10, 5))
    plt.errorbar(x, collision_rates_means, yerr=collision_rates_stds, fmt='o', capsize=5, elinewidth=2,
                 markeredgewidth=2)
    plt.xticks(x, ['ALOHA', 'CSMA'])
    plt.title('Collision Rate with Error Bars')
    plt.xlabel('Protocol')
    plt.ylabel('Collision Rate')
    plt.show()
