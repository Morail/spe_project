import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats as st
from statsmodels import api as sm


def compute_percentiles(data, percentiles):
    # Specify array of percentiles: percentiles
    if not percentiles:
        # Default value
        percentiles = np.array([2.5, 25, 50, 75, 97.5])
    # Compute percentiles:
    return np.percentile(data, percentiles)


def compute_mean(data):
    return np.mean(data)


def compute_std(data):
    return np.std(data)


def manual_computation_std(data):
    # Compute the mean
    m = np.mean(data)
    # Compute array with differences from data items and their mean
    diff = data - m
    # Square previously obtained array
    diff_sqr = diff**2
    # Compute the mean and obtain the variance
    var = np.mean(diff_sqr)
    # Std is the square root of the variance
    std = np.sqrt(var)
    return std


def compute_variance(data):
    return np.var(data)


def manual_computation_variance(data):
    # Compute the mean
    m = np.mean(data)
    # Compute array with differences from data items and their mean
    diff = data - m
    # Square previously obtained array
    diff_sqr = diff**2
    # Compute the mean and obtain the variance
    var = np.mean(diff_sqr)
    return var


def compute_median(data):
    return np.median(data)


def compute_confidence_interval(data, confidence=0.95):

    mean = np.mean(data)
    sem = st.sem(data)
    interval = st.t.interval(confidence, len(data) - 1, loc=mean, scale=sem)

    return mean, interval


def plot_histogram(data_, metric, protocol, num_stations, bins=20, save_fig=False):

    # Throughput histogram
    title = '%s %s for %d stations' % (protocol.upper(), metric, num_stations)
    # Seaborn
    sns.histplot(data=data_, x=metric, bins=bins, kde=True).set_title(title)

    if save_fig:
        fn_ = './plots/%s_%s_%d_histogram.png' % (protocol, metric, num_stations)
        plt.savefig(fn_, bbox_inches='tight')

    plt.show()


def plot_scatterplot(data_, x, y, save_fig=False):
    sns.set_theme(style="white", color_codes=True)

    # Use JointGrid directly to draw a custom plot
    g = sns.JointGrid(data=data_, x=x, y=y, space=0, ratio=17)
    g.plot_joint(sns.scatterplot, size=data_[x], sizes=(30, 120),
                 color="g", alpha=.6, legend=False)
    g.plot_marginals(sns.rugplot, height=1, color="g", alpha=.6)


def plot_catplot(data_, protocol, save_fig=False):

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


def plot_qqplot(data_, metric, title, fname=None, save_fig=False):
    sns.set_theme()

    _ = sm.qqplot(data_[metric], line='45')

    plt.title(title)

    if save_fig:
        plt.savefig(fname, bbox_inches='tight')

    plt.show()


def plot_ecdf(data_, metric, title='ECDF', fname=None, save_fig=False):
    sns.set_theme()

    x, y = ecdf(data_[metric])

    _ = plt.plot(x, y, marker='.', linestyle='none')
    _ = plt.xlabel(metric)
    _ = plt.ylabel("ECDF")
    plt.title(title)

    # Keeps data off plot edges by adding a 2% buffer all around the plot
    plt.margins(0.02)

    if save_fig:
        plt.savefig(fname, bbox_inches='tight')

    plt.show()


def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    n = len(data)

    # x-data for the ECDF: sorting of input data
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n

    return x, y
