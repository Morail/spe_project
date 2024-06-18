from random import Random

import aloha
import utils
import csma
import config


def main():

    # Retrieve the configuration parameters for this simulation
    cfg = config.Config('./config.ini')

    # Set seed
    Random.seed(cfg.seed)

    # Init logger
    is_debug = True
    log_ = utils.init_logger(is_debug=is_debug)

    # Stats for the different simulations' config
    stats_ = {ns: {'aloha': {}, 'csma': {}} for ns in cfg.num_stations}

    # Iterate over the different elements of the NUM_STATIONS list
    for ns in cfg.num_stations:

        # Run ALOHA simulations
        stats_[ns]['aloha'] = aloha.run_simulations(cfg.num_runs, ns, cfg.num_epochs, cfg.max_backoff_time, log_)

        # Run CSMA simulations
        stats_[ns]['csma'] = csma.run_simulations(cfg.num_runs, ns, cfg.num_epochs, cfg.max_backoff_time, log_)

        # Print some stats jus for debug purposes
        if is_debug:
            for p, s in stats_[ns].items():
                for k, v in s.items():
                    # Do not print stats that are either None or a list
                    if v is not None and not isinstance(v, list):
                        log_.debug("[%s] :: Number of station: %d - Stats: %s: %s" % (p.upper(), ns, k.upper(), v))

    # Plot statistics
    # utils.plot_results(aloha_throughputs, csma_throughputs, aloha_collision_rates, csma_collision_rates)
    utils.plot_stats(stats_, cfg.num_stations)

    print(print(utils.print_tables(stats_, 'throughput')))
    print(print(utils.print_tables(stats_, 'collision_rate')))
    print(print(utils.print_tables(stats_, 'delay')))


if __name__ == "__main__":
    main()
