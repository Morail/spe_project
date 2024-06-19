import math

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats as st
from statsmodels import api as sm


def compute_percentiles(data, percentiles):
    # Specify array of percentiles: percentiles
    if percentiles is None or len(percentiles) == 0:
        # Default value
        percentiles = np.array([2.5, 25, 50, 75, 97.5])
    # Compute percentiles:
    return np.percentile(data, percentiles)


def compute_mean(data):
    return np.mean(data)


def compute_std(data):
    return np.std(data)


def manual_computation_std(data):
    # Obtain the variance
    var = manual_computation_variance(data)
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
    diff_sqr = diff ** 2
    # Compute the mean and obtain the variance
    var = np.mean(diff_sqr)
    return var


def compute_median(data):
    return np.median(data)


def compute_confidence_interval(data, confidence=0.95):
    """Compute given confidence interval."""
    mean = np.mean(data)
    sem = st.sem(data)
    interval = st.t.interval(confidence, len(data) - 1, loc=mean, scale=sem)

    return mean, interval


def compute_ci_median(data):
    """The following holds for larger sample set ( > 71)"""
    n = len(data)
    sdata = np.sort(data)

    lower = math.floor((0.50*n) - (0.980*math.sqrt(n)))
    upper = math.ceil((0.50*n) +1 + (0.980*math.sqrt(n)))

    interval = [sdata[lower], sdata[upper]]
    mean = compute_mean(data)

    return mean, interval


def compute_gini_coefficient(data):
    """Compute Gini coefficient of array of values"""
    data = np.double(data)
    data = data / sum(data)
    # Mean absolute difference
    mad = np.abs(np.subtract.outer(data, data)).mean()
    # Relative mean absolute difference
    rmad = mad / np.mean(data)
    # Gini coefficient
    g = 0.5 * rmad
    return g


def compute_coefficient_of_variation(data):
    cov = np.std(data) / np.mean(data)
    return cov


def compute_mad(data):
    """Mean Absolute Deviation"""
    m = compute_mean(data)
    n = len(data)
    mad = sum(abs(data - m)) / n

    return mad


def compute_lorenz_curve_gap(data):
    """Lorenz Curve Gap is a rescaled version of MAD. Alternative to CoV,
    it uses mean absolute deviation."""
    m = compute_mean(data)
    mad = compute_mad(data)

    gap = mad / (2*m)

    return gap


def plot_histogram(data_, metric, protocol, num_stations, bins=20, save_fig=False):
    # Throughput histogram
    title = '%s %s for %d stations' % (protocol.upper(), metric, num_stations)
    # Seaborn
    sns.histplot(data=data_, x=metric, bins=bins, kde=True).set_title(title)

    if save_fig:
        fn_ = './plots/%s_%s_%d_histogram.png' % (protocol, metric, num_stations)
        plt.savefig(fn_, bbox_inches='tight')

    plt.show()


def plot_lorenz_curve(data_, title, fname, save_fig=False):
    """The curve is a graph showing the proportion of overall income or wealth
    assumed by the bottom x % of the people"""
    sns.set()

    m = compute_mean(data_)
    sdata = np.sort(data_)
    n = len(data_)

    z = n * m

    lorenz_curve = np.sort([(sum(sdata[:i + 1]) / n * m) for i, d in enumerate(sdata)])
    # lorenz_curve = sdata.cumsum() / z

    fig, ax = plt.subplots(figsize=[6, 6])
    ## scatter plot of Lorenz curve
    ax.scatter(np.arange(lorenz_curve.size) / (lorenz_curve.size - 1), lorenz_curve,
               marker='x', color='darkgreen', s=100)
    ## line plot of equality
    ax.plot([0, 1], [0, 1], color='k')

    plt.title(title)

    if save_fig:
        plt.savefig(fname, bbox_inches='tight')

    plt.show()


def plot_scatterplot(data_, x, y, save_fig=False):
    sns.set_theme(style="white", color_codes=True)

    # Use JointGrid directly to draw a custom plot
    g = sns.JointGrid(data=data_, x=x, y=y, space=0, ratio=17)
    g.plot_joint(sns.scatterplot, size=data_[x], sizes=(30, 120),
                 color="g", alpha=.6, legend=False)
    g.plot_marginals(sns.rugplot, height=1, color="g", alpha=.6)


def plot_catplot(data_, protocol, save_fig=False):
    sns.set()
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
    y = np.arange(1, n + 1) / n

    return x, y
