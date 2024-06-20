import math

import numpy as np
import scipy.stats
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats as st
import pandas as pd


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

    return interval


def compute_ci_median(data):
    """The following holds for larger sample set ( > 71)"""
    n = len(data)
    sdata = np.sort(data)

    lower = math.floor((0.50 * n) - (0.980 * math.sqrt(n)))
    upper = math.ceil((0.50 * n) + 1 + (0.980 * math.sqrt(n)))

    interval = [sdata[lower], sdata[upper]]
    mean = compute_mean(data)

    return interval


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

    gap = mad / (2 * m)

    return gap


def rescale_data(data):
    """Apply the Box-Cox transformation to given data. Data is best rescaled"""
    t_data = scipy.stats.boxcox(data)

    return t_data


def plot_histogram(data_, metric, protocol, num_stations, bins=20, save_fig=False):
    # Throughput histogram
    title = '%s %s %d stations' % (protocol.upper(), metric, num_stations)
    # Seaborn
    sns.histplot(data=data_, x=metric, bins=bins, kde=True).set_title(title)

    if save_fig:
        fn_ = './plots/%s_%s_%d_histogram.png' % (protocol, metric, num_stations)
        plt.savefig(fn_, bbox_inches='tight')
    else:
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
    else:
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


def plot_qqplot(data, title, fname=None, save_fig=False):
    sns.set()

    x = np.array(data)

    # MLE to find parameter p for geometric distribution
    dist = scipy.stats.geom
    # Test for geometric distribution
    # TODO: check for others
    # TODO: chi-square test
    res = scipy.stats.fit(dist, data)
    # print(res)
    # Set ditribution params
    params = res.params if res.success else (0.02)  # 0.02 default value after observation

    fig = plt.figure()
    props = dict(boxstyle='round', alpha=0.5, fill=True, color="blue")
    ax1 = fig.add_subplot(211)
    ax1.set_xlabel('')
    ax1.set_title('Probplot against geometric distribution')
    ax1.text(0.05, 0.90, "Data vs geometric", transform=ax1.transAxes, fontsize=14,
             verticalalignment='top', bbox=props)
    _ = scipy.stats.probplot(x, dist=scipy.stats.geom, sparams=params, plot=ax1, fit=True)
    ax2 = fig.add_subplot(212)
    ax2.set_title('Probplot after Box-Cox transformation')
    try:
        xt, _ = rescale_data(data)
        _ = scipy.stats.probplot(xt, dist=scipy.stats.norm, plot=ax2, fit=True)
        ax2.text(0.05, 0.85, "Rescaled Data vs norm", transform=ax2.transAxes, fontsize=14,
                 verticalalignment='top', bbox=props)
    except ValueError:
        print('Error: can not plot rescaled data qq-plot')

    # _ = sm.qqplot(x, line='45')
    # plot = sm.ProbPlot(x, dist=scipy.stats.geom, distargs=(1/3,))
    # plot = sm.ProbPlot(x, dist=scipy.stats.lognorm, fit=True)
    # plot.qqplot(line='45')

    if save_fig:
        plt.savefig(fname, bbox_inches='tight')
    else:
        plt.show()


def plot_boxplot(data, title="Boxplot", fname=None, save_fig=False):
    sns.set()

    df = pd.DataFrame(data, columns=['sampled', 'rescaled'])

    # plt.figure(figsize=(9,9)) #for a bigger image
    sns.boxplot(x="variable", y="value", data=pd.melt(df), showfliers=False,
                notch=True, #flierprops={"marker": "x"},
                boxprops={"facecolor": (.3, .5, .7, .5)},
                legend="full",
                medianprops={"color": "r", "linewidth": 2})
    # df.boxplot(showfliers=False)
    plt.title(title)

    if save_fig:
        plt.savefig(fname, bbox_inches='tight')
    else:
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
    else:
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
