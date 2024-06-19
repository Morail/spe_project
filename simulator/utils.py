import logging
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
import seaborn as sns

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


def plot_histogram(data_, metric, protocol, num_stations, bins=20, save_fig=False):

    # Throughput histogram
    title = '%s %s for %d stations' % (protocol.upper(), metric, num_stations)
    # Seaborn
    sns.histplot(data=data_, x=metric, bins=bins, kde=False).set_title(title)

    # Matplotlib
    #_ = plt.hist(data_, bins=bins)
    #_ = plt.xlabel(xlabel)
    #_ = plt.ylabel(ylabel)
    #_ = plt.title(title)

    if save_fig:
        fn_ = './plots/%s_%s_%d_histogram.png' % (protocol, metric, num_stations)
        plt.savefig(fn_, bbox_inches='tight')

    plt.show()


def plot_scatterplot(data_, x, y):
    sns.set_theme(style="white", color_codes=True)

    # Use JointGrid directly to draw a custom plot
    g = sns.JointGrid(data=data_, x=x, y=y, space=0, ratio=17)
    g.plot_joint(sns.scatterplot, size=data_[x], sizes=(30, 120),
                 color="g", alpha=.6, legend=False)
    g.plot_marginals(sns.rugplot, height=1, color="g", alpha=.6)

def plot_catplot(data_, protocol):

    sns.set_theme(style="whitegrid")

    # Load the example exercise dataset
    exercise = sns.load_dataset("exercise")

    # Draw a pointplot to show pulse as a function of three categorical factors
    g = sns.catplot(
        data=data_, x="time", y="pulse", hue="protocol", col="diet",
        capsize=.2, palette="YlGnBu_d", errorbar="se",
        kind="point", height=6, aspect=.75,
    )
    g.despine(left=True)


def plot_ecdf(data_, metric, title='ECDF', fname=None):
    sns.set_theme()

    # Sort data for the x axis
    x = np.sort(data_[metric])
    # Arange return evenly spaced values within a given interval
    y = np.arange(1, len(x)+1) / len(x)

    _ = plt.plot(x, y, marker='.', linestyle='none')
    _ = plt.xlabel(metric)
    _ = plt.ylabel("ECDF")
    plt.title(title)

    # Keeps data off plot edges by adding a 2% buffer all around the plot
    plt.margins(0.02)

    if fname is not None:
        plt.savefig(fname, bbox_inches='tight')

    plt.show()


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
