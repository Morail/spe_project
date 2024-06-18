import random
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

        for txs in transmitting:
            txs.start_tx()
            # Commence transmission
            channel.transmit(txs.packet_size)

        # Only one node is trying to transmit on the channel
        if len(transmitting) == 1:
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


def run_simulations(num_stations, cfg, rng_, logger):
    logger.info("[ALOHA] :: Running %d simulations with %d stations" % (cfg.num_runs, num_stations))

    throughputs = []
    collision_rates = []
    waiting_times = []
    lost_packets = []
    tx_packets = []

    for _ in range(cfg.num_runs):

        if (_ + 1) % 100 == 0:
            logger.debug("[ALOHA] :: Run number %d" % (_ + 1))

        # Generate rvs for each station in the simulated model for the three different categories
        # TODO: define upper and lower interval bound using the config file
        packet_probs = [rng_.generate_random_uniform(0.05, 0.4) for _ in range(num_stations)]
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

    # Retrieve the configuration parameters for this simulation
    cfg = config.Config('./config.ini')

    # Init Random Number Generator
    rng_ = rng.RandomNumberGenerator(cfg.seed)

    # Create logger
    log_ = utils.init_logger(is_debug=cfg.is_debug)

    # Stats for the different simulations' config
    stats_ = {ns: {'aloha': {}, 'csma': {}} for ns in cfg.list_num_stations}

    for ns in cfg.list_num_stations:

        # Run simulation with the given parameter and the "ns" number of stations
        # The number of station is the only variable in the simulation
        stats_[ns]['aloha'] = run_simulations(ns, cfg, rng_, log_)

        # Debug purposes only
        log_.debug(stats_[ns]['aloha'])

        log_.info("[ALOHA] :: Average Throughput: %s" % (stats_[ns]['aloha'].get('avg_throughput')))
        log_.info("[ALOHA] :: Average Collision Rate: %s" % (stats_[ns]['aloha'].get('avg_collision_rate')))
        log_.info("[ALOHA] :: Average Waiting Time: %s" % (stats_[ns]['aloha'].get('avg_waiting_times')))
        log_.info("[ALOHA] :: Average Transmitted packets: %s" % (stats_[ns]['aloha'].get('avg_tx_packets')))
        log_.info("[ALOHA] :: Average Lost packets: %s" % (stats_[ns]['aloha'].get('avg_lost_packets')))

    # Plot results
    utils.plot_stats(stats_, cfg.list_num_stations)


if __name__ == "__main__":
    main()
