import numpy as np

import stats
import utils
import aloha
import csma
import config


def print_stats(df, log_, protocol, num_stations, metric):

    percentiles = stats.compute_percentiles(df, np.array([2.5, 25, 75, 97.5]))
    mean = stats.compute_mean(df)
    median = stats.compute_median(df)
    variance = stats.compute_variance(df)
    std = stats.compute_std(df)
    ci = stats.compute_confidence_interval(df)
    ci95 = stats.compute_ci_median(df)
    gini = stats.compute_gini_coefficient(df)
    cov = stats.compute_coefficient_of_variation(df)
    mad = stats.compute_mad(df)
    gap = stats.compute_lorenz_curve_gap(df)

    log_.info("[%s] - [%d stations] :: %s mean: %s" % (protocol.upper(), num_stations, metric, mean))
    log_.info("[%s] - [%d stations] :: %s median: %s" % (protocol.upper(), num_stations, metric, median))
    log_.info("[%s] - [%d stations] :: %s percentiles: %s" % (protocol.upper(), num_stations, metric, percentiles))
    log_.info("[%s] - [%d stations] :: %s variance: %s" % (protocol.upper(), num_stations, metric, variance))
    log_.info("[%s] - [%d stations] :: %s std: %s" % (protocol.upper(), num_stations, metric, std))
    log_.info("[%s] - [%d stations] :: %s ci: %s" % (protocol.upper(), num_stations, metric, ci))
    log_.info("[%s] - [%d stations] :: %s ci95: %s" % (protocol.upper(), num_stations, metric, ci95))
    log_.info("[%s] - [%d stations] :: %s gini: %s" % (protocol.upper(), num_stations, metric, gini))
    log_.info("[%s] - [%d stations] :: %s CoV: %s" % (protocol.upper(), num_stations, metric, cov))
    log_.info("[%s] - [%d stations] :: %s mad: %s" % (protocol.upper(), num_stations, metric, mad))
    log_.info("[%s] - [%d stations] :: %s gap: %s" % (protocol.upper(), num_stations, metric, gap))

def start_simulations(protocols):

    # Retrieve the configuration parameters for this simulation
    cfg = config.Config('./config.ini')

    # Create logger
    log_ = utils.init_logger(is_debug=cfg.is_debug)

    # Stats for the different simulations' config
    simulations_res = {ns: {'aloha': {}, 'csma': {}} for ns in cfg.list_num_stations}

    # Iterate over the different protocols
    for protocol in protocols:

        # Iterate over the different number of devices as specified in the simulation's config
        for num_stations in cfg.list_num_stations:

            # Run simulation with the given parameter and the "ns" number of stations
            # The number of station is the only variable in the simulation
            if protocol == 'aloha':
                simulations_res[num_stations][protocol] = aloha.run_simulations(num_stations, cfg, log_)
            # elif protocol == 'csma':
            #    simulations_res[num_stations][protocol] = csma.run_simulations(num_stations, cfg, log_)
            else:
                log_.error("Protocol %s not supported" % protocol)
                continue

            # Load results into a DataFrame
            data_ = utils.load_df(simulations_res[num_stations][protocol])

            for metric, df in simulations_res[num_stations][protocol].items():

                if df is None:
                    log_.error("Can not compute any statistic for protocol %s and %s metric" % (protocol, metric))

                log_.debug("Processing metric %s" % metric)

                # Rescale data via Box-Cox transformation
                t_data = stats.rescale_data(df)

                print_stats(df, log_, protocol, num_stations, metric)

                # print_stats(t_data, log_, protocol, num_stations, metric)

                # Plot graphs
                # Save plots to file system only if log level is not DEBUG
                save_fig = not cfg.is_debug

                # Histogram
                # Number of bins chosen as the square roots of the number of samples
                n_bins = round(np.sqrt(cfg.num_runs))
                # Plot histograms for each metric
                stats.plot_histogram(data_, metric, protocol, num_stations, n_bins, save_fig)

                # ECDF
                title = '%s %s ECDF for %d stations' % (protocol.upper(), metric, num_stations)
                fn_ = './plots/%s_%s_%d_ecdf.png' % (protocol, metric, num_stations)
                stats.plot_ecdf(data_, metric, title=title, fname=fn_, save_fig=save_fig)

                # qqplot
                title = '%s %s qqplot for %d stations' % (protocol.upper(), metric, num_stations)
                fn_ = './plots/%s_%s_%d_qqplot.png' % (protocol, metric, num_stations)
                stats.plot_qqplot(df, title=title, fname=fn_, save_fig=save_fig)

                # Lorenz Curve
                title = '%s %s Lorenz Curve for %d stations' % (protocol.upper(), metric, num_stations)
                fn_ = './plots/%s_%s_%d_lorenz.png' % (protocol, metric, num_stations)
                # stats.plot_lorenz_curve(data_, title, fname=fn_, save_fig=save_fig)

    # Plot results
    # utils.plot_stats(stats_, cfg.list_num_stations)


def main():

    # Start running the simulations for both protocols
    start_simulations(['aloha', 'csma'])


if __name__ == "__main__":
    main()
