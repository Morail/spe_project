import numpy as np

import stats
import utils
import aloha
import csma
import config


def compute_stats(df, log_, protocol, num_stations, obs):

    s = {
        'protocol': protocol
        , 'num_stations': num_stations
        , 'obs': obs
        , 'percentiles': " - ".join([str("{:.2f}".format(x)) for x in stats.compute_percentiles(df, np.array([2.5, 25, 75, 97.5]))])
        , 'mean': stats.compute_mean(df)
        , 'median': stats.compute_median(df)
        , 'var': stats.compute_variance(df)
        , 'std': stats.compute_std(df)
        , 'ci': " - ".join(str("{:.2f}".format(x)) for x in stats.compute_confidence_interval(df))
        , 'CIs median': " - ".join(str("{:.2f}".format(x)) for x in stats.compute_ci_median(df))
        , 'gini': stats.compute_gini_coefficient(df)
        , 'CoV': stats.compute_coefficient_of_variation(df)
        , 'mad': stats.compute_mad(df)
        , 'gap': stats.compute_lorenz_curve_gap(df)
    }

    log_.info("[%s] - [%d stations] :: stats %s" % (protocol.upper(), num_stations, s))

    return s


def start_simulations(protocols):

    # Retrieve the configuration parameters for this simulation
    cfg = config.Config('./config.ini')

    # Create logger
    log_ = utils.init_logger(is_debug=cfg.is_debug)

    # Stats for the different simulations' config
    simulations_res = {ns: {'aloha': {}, 'csma': {}} for ns in cfg.list_num_stations}
    overall_stats = []

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
                try:
                    t_data = stats.rescale_data(df)
                except ValueError:
                    log_.error("Con not rescale data for protocol %s and %s metric" % (protocol, metric))

                overall_stats.append(compute_stats(df, log_, protocol, num_stations, metric))

                # Plot graphs
                # Save plots to file system only if log level is not DEBUG
                save_fig = not cfg.is_debug

                # Histogram
                # Number of bins chosen as the square roots of the number of samples
                n_bins = round(np.sqrt(cfg.num_runs))
                # Plot histograms for each metric
                stats.plot_histogram(data_, metric, protocol, num_stations, n_bins, save_fig)

                # ECDF
                title = '%s %s %d stations' % (protocol.upper(), metric, num_stations)
                fn_ = './plots/%s_%s_%d_ecdf.png' % (protocol, metric, num_stations)
                stats.plot_ecdf(data_, metric, title=title, fname=fn_, save_fig=save_fig)

                # qqplot
                title = '%s %s %d stations' % (protocol.upper(), metric, num_stations)
                fn_ = './plots/%s_%s_%d_qqplot.png' % (protocol, metric, num_stations)
                stats.plot_qqplot(df, title=title, fname=fn_, save_fig=save_fig)

                # Lorenz Curve
                title = '%s %s Lorenz Curve for %d stations' % (protocol.upper(), metric, num_stations)
                fn_ = './plots/%s_%s_%d_lorenz.png' % (protocol, metric, num_stations)
                # stats.plot_lorenz_curve(data_, title, fname=fn_, save_fig=save_fig)

                # TODO: chi-squared test the observed sample

    # Plot results
    # utils.plot_stats(stats_, cfg.list_num_stations)

    # Print overall stats in a table-fashioned way
    utils.print_tables(overall_stats, log_, save_fig)


def main():

    # Start running the simulations for both protocols
    start_simulations(['aloha', 'csma'])


if __name__ == "__main__":
    main()
