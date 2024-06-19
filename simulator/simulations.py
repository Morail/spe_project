import numpy as np

import stats
import utils
import aloha
import csma
import config


def start_simulations(protocols):

    # Retrieve the configuration parameters for this simulation
    cfg = config.Config('./config.ini')

    # Create logger
    log_ = utils.init_logger(is_debug=cfg.is_debug)

    # Stats for the different simulations' config
    simulations_res = {ns: {'aloha': {}, 'csma': {}} for ns in cfg.list_num_stations}

    for protocol in protocols:
        for num_stations in cfg.list_num_stations:

            # Run simulation with the given parameter and the "ns" number of stations
            # The number of station is the only variable in the simulation
            if protocol == 'aloha':
                simulations_res[num_stations][protocol] = aloha.run_simulations(num_stations, cfg, log_)
            elif protocol == 'csma':
                simulations_res[num_stations][protocol] = csma.run_simulations(num_stations, cfg, log_)
            else:
                log_.error("Protocol %s not supported" % protocol)
                continue

            # Load results into a DataFrame
            data_ = utils.load_df(simulations_res[num_stations][protocol])

            for metric, df in simulations_res[num_stations][protocol].items():

                if df is None:
                    log_.error("Can not compute any statistic for protocol %s and %s metric" % (protocol, metric))

                log_.debug("Processing metric %s" % metric)

                percentiles = stats.compute_percentiles(df)
                mean = stats.compute_mean(df)
                median = stats.compute_median(df)
                variance = stats.compute_variance(df)
                std = stats.compute_std(df)

                log_.info("[%s] :: %s mean: %s" % (protocol.upper(), metric, mean))
                log_.info("[%s] :: %s median: %s" % (protocol.upper(), metric, median))
                log_.info("[%s] :: %s percentiles: %s" % (protocol.upper(), metric, percentiles))
                log_.info("[%s] :: %s variance: %s" % (protocol.upper(), metric, variance))
                log_.info("[%s] :: %s std: %s" % (protocol.upper(), metric, std))

                # Plot graphs
                # Save plots to file system only if log level is not DEBUG
                save_fig = not cfg.is_debug

                # Plot HISTOGRAM
                # Number of bins chosen as the square roots of the number of samples
                n_bins = round(np.sqrt(cfg.num_runs))
                # Plot histograms for each metric
                stats.plot_histogram(data_, metric, protocol, num_stations, n_bins, save_fig)

                # Plot ECDF
                title = '%s %s ECDF for %d stations' % (protocol.upper(), metric, num_stations)
                # Save plot to plots directory, only if is_debug is set to False
                fn_ = './plots/%s_%s_%d_ecdf.png' % (protocol, metric, num_stations) if not cfg.is_debug else None
                stats.plot_ecdf(data_, metric, title=title, fname=fn_)

                # Plot QQPLOT
                title = '%s %s qqplot for %d stations' % (protocol.upper(), metric, num_stations)
                # Save plot to plots directory, only if is_debug is set to False
                fn_ = './plots/%s_%s_%d_qqplot.png' % (protocol, metric, num_stations) if not cfg.is_debug else None
                stats.plot_qqplot(data_, metric, title=title, fname=fn_)

    # Plot results
    # utils.plot_stats(stats_, cfg.list_num_stations)


def main():

    # Start running the simulations for both protocols
    start_simulations(['aloha', 'csma'])


if __name__ == "__main__":
    main()
