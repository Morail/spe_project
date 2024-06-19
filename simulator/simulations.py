import aloha
import utils
import csma
import config
import rng


def main():

    # Retrieve the configuration parameters for this simulation
    cfg = config.Config('./config.ini')

    # Init logger
    log_ = utils.init_logger(is_debug=cfg.is_debug)

    # Stats for the different simulations' config
    stats_ = {ns: {'aloha': {}, 'csma': {}} for ns in cfg.list_num_stations}

    # Iterate over the different elements of the NUM_STATIONS list
    for num_stations in cfg.list_num_stations:

        # Run ALOHA simulations
        stats_[num_stations]['aloha'] = aloha.run_simulations(num_stations, cfg, log_)

        # Run CSMA simulations
        # stats_[num_stations]['csma'] = csma.run_simulations(num_stations, cfg, log_)

        # Print some stats jus for debug purposes
        if cfg.is_debug:
            for p, s in stats_[num_stations].items():
                for k, v in s.items():
                    # Do not print stats that are either None or a list
                    if v is not None and not isinstance(v, list):
                        log_.debug("[%s] :: Nr. of stations: %d - Stats: %s: %s" % (p.upper(), num_stations, k.upper(), v))

    # Plot statistics
    # utils.plot_results(aloha_throughputs, csma_throughputs, aloha_collision_rates, csma_collision_rates)
    utils.plot_stats(stats_, cfg.list_num_stations)

    print(print(utils.print_tables(stats_, 'throughput')))
    print(print(utils.print_tables(stats_, 'collision_rate')))
    print(print(utils.print_tables(stats_, 'delay')))


if __name__ == "__main__":
    main()
