from channel import Channel
import numpy as np

import config
import utils
import rng
import stats


def sim_aloha(num_nodes, cfg, packet_probs, transmission_times, packet_sizes, rng_, logger):
    total_transmissions = 0

    channel = Channel()
    stations = utils.init_stations(num_nodes, packet_probs, packet_sizes, rng_, cfg.max_backoff_time)

    for slot in range(cfg.num_epochs):

        # Only for debug purposes
        if (slot + 1) % 1000 == 0:
            logger.debug(("Processing %d slot" % (slot + 1)))

        # List of stations ready to transmit a frame
        transmitting = [s for s in stations if s.has_frame_to_transmit()]

        # List of nodes waiting for the backoff time to be over
        waiting = [s for s in stations if s.is_waiting()]

        # Keep count of transmission
        total_transmissions += len(transmitting)

        if not transmitting:
            # No nodes ready to start a trasmission
            continue

        # Iterate over all the stations in TX=transmit state
        for txs in transmitting:
            txs.start_tx()
            # Start transmission
            channel.transmit(txs.packet_size)

        # Only one node is trying to transmit on the channel
        if len(transmitting) == 1:
            # There is only one station in the TX state
            s = transmitting[0]
            # Ack the sender
            s.get_ack()
            # Deliver the package, free the channel
            channel.deliver()
        else:
            # Multiple nodes are trying to send over the channel, this lead to a collision
            # Debug purposes
            logger.debug("Slot %d : collision detected between %d nodes" % (slot + 1, len(transmitting)))
            logger.debug('Colliding nodes: %s' % ', '.join(str(t) for t in transmitting))

            # In case of collision sent packets are lost
            for txs in transmitting:
                # Sending station has to handle with the collision
                txs.handle_collision()

        # Decrease waiting time for stations in WAIT state, as a way to
        # simulate the increase in the time clock 
        # Once waiting time is back to 0 the station will be
        # ready to retransmit the package
        for w in waiting:
            w.decrease_waiting_time()

    waiting_time = np.mean(sum([s.waiting_time for s in stations]))
    throughput = channel.transmission_size / cfg.num_epochs
    collision_rate = (total_transmissions - channel.packets_delivered) / total_transmissions
    lost_packets = np.mean(sum([s.lost_packets for s in stations]))

    return throughput, collision_rate, channel.packets, total_transmissions, waiting_time, lost_packets


def run_simulations(num_stations, cfg, logger):
    logger.info("[ALOHA] :: Running %d simulations with %d stations" % (cfg.num_runs, num_stations))

    throughputs = []
    collision_rates = []
    waiting_times = []
    lost_packets = []
    tx_packets = []

    for _ in range(cfg.num_runs):

        # Init Random Number Generator
        # Independent replications: re-initialize each replication with a different RNG seed
        rng_ = rng.RandomNumberGenerator()
        # Alternative: initialize with fixed seed in order to ensure reproducibility of the simulation
        # rng_ = rng.RandomNumberGenerator(cfg.seed)

        if (_ + 1) % 100 == 0:
            logger.debug("[ALOHA] :: Run number %d" % (_ + 1))

        # Generate rvs for each station in the simulated model for the three different categories
        # TODO: define upper and lower interval bound using the config file
        packet_probs = [rng_.generate_random_uniform(0.01, 0.2) for _ in range(num_stations)]
        transmission_times = [rng_.generate_random_int(1, 3) for _ in range(num_stations)]
        packet_sizes = [rng_.generate_random_int(50, 1500) for _ in range(num_stations)]

        tput, c_rate, tx_pack, _, w_time, l_packs = sim_aloha(num_stations, cfg, packet_probs,
                                                              transmission_times,
                                                              packet_sizes, rng_, logger)
        throughputs.append(tput)
        collision_rates.append(c_rate)
        waiting_times.append(w_time)
        lost_packets.append(l_packs)
        tx_packets.append(tx_pack)

    return {
        "average_throughput": np.mean(throughputs),
        "average_collision_rate": np.mean(collision_rates),
        "throughput": throughputs,
        "collision_rate": collision_rates,
        "delay": waiting_times,
        "lost_packets": lost_packets,
        "tx_packets": tx_packets,
        "avg_delay": np.mean(waiting_times),
        "avg_lost_packets": np.mean(lost_packets),
        "avg_tx_packets": np.mean(tx_packets),
        "avg_utilization": None,
        "avg_retransmissions": None
    }


def main():

    protocol = 'aloha'

    # Retrieve the configuration parameters for this simulation
    cfg = config.Config('./config.ini')

    # Create logger
    log_ = utils.init_logger(is_debug=cfg.is_debug)

    # Stats for the different simulations' config
    res = {ns: {'aloha': {}, 'csma': {}} for ns in cfg.list_num_stations}

    for num_stations in cfg.list_num_stations:

        # Run simulation with the given parameter and the "ns" number of stations
        # The number of station is the only variable in the simulation
        res[num_stations][protocol] = run_simulations(num_stations, cfg, log_)

        # Debug purposes only
        log_.debug(res[num_stations][protocol])

        log_.info("[ALOHA] :: Average Throughput: %s" % (res[num_stations][protocol].get('avg_throughput')))
        log_.info("[ALOHA] :: Average Collision Rate: %s" % (res[num_stations][protocol].get('avg_collision_rate')))
        log_.info("[ALOHA] :: Average Waiting Time: %s" % (res[num_stations][protocol].get('avg_waiting_times')))
        log_.info("[ALOHA] :: Average Transmitted packets: %s" % (res[num_stations][protocol].get('avg_tx_packets')))
        log_.info("[ALOHA] :: Average Lost packets: %s" % (res[num_stations][protocol].get('avg_lost_packets')))

        # Load results into a DataFrame
        data_ = stats.load_df(res[num_stations][protocol])

        # Plot graphs
        # Save plots to file system only if log level is not DEBUG
        save_fig = not cfg.is_debug

        # Throughput histogram
        # Number of bins chosen as the square roots of the number of samples
        n_bins = round(np.sqrt(cfg.num_runs))
        # Plot histograms for each metric
        utils.plot_histogram(data_, 'throughput', protocol, num_stations, n_bins, save_fig)
        utils.plot_histogram(data_, 'delay', protocol, num_stations, n_bins, save_fig)
        utils.plot_histogram(data_, 'collision_rate', protocol, num_stations, num_stations, save_fig)
        utils.plot_histogram(data_, 'lost_packets', protocol, num_stations, num_stations, save_fig)
        utils.plot_histogram(data_, 'tx_packets', protocol, num_stations, n_bins, save_fig)

        # Plot ECDF
        title = '%s ECDF for %d stations' % (protocol.upper(), num_stations)
        # Save plot to plots directory, only if is_debug is set to False
        fn_ = './plots/%s_throughput_%d_ecdf.png' % (protocol, num_stations) if not cfg.is_debug else None
        utils.plot_ecdf(data_, 'throughput', title=title, fname=fn_)

    # Plot results
    #utils.plot_stats(stats_, cfg.list_num_stations)


if __name__ == "__main__":
    main()
