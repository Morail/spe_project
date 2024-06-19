from channel import Channel
import numpy as np

import utils
import simulations
import rng


def sim_csma(num_nodes, cfg, packet_probs, transmission_times, packet_sizes, rng_, logger):
    successful_transmissions = 0
    total_transmissions = 0
    total_data_transmitted = 0
    channel_time_remaining = 0
    collisions = 0

    c = Channel()
    stations = utils.init_stations(num_nodes, packet_probs, packet_sizes, rng_, cfg.max_backoff_time)

    for slot in range(cfg.num_epochs):

        # Only for debug purposes
        if (slot + 1) % 1000 == 0:
            logger.debug(("Processing %d slot" % (slot + 1)))

        # List of stations ready to transmit a frame
        transmitting = [s for s in stations if s.has_frame_to_transmit()]

        for s in stations:
            if s.has_frame_to_transmit():
                if not c.is_busy:
                    c.transmit(s.packet_size)
                    transmissions += 1
                    transmitting_nodes.append(s)

        if c.is_busy:
            channel_time_remaining -= 1
            if channel_time_remaining <= 0:
                c.set_busy(False)

        if transmissions > 0:
            total_transmissions += transmissions
            if transmissions == 1:
                successful_transmissions += 1
                c.set_busy()
                node_index = stations.index(transmitting_nodes[0])
                channel_time_remaining = transmission_times[node_index]
                total_data_transmitted += packet_sizes[node_index]

    waiting_time = np.mean(sum([s.waiting_time for s in stations]))
    throughput = total_data_transmitted / cfg.num_epochs
    collision_rate = (total_transmissions - successful_transmissions) / total_transmissions
    return throughput, collision_rate, successful_transmissions, total_transmissions, waiting_time


def run_simulations(num_stations, cfg, logger):
    logger.info("[CSMA]  :: Running %d simulations with %d stations" % (cfg.num_runs, num_stations))

    throughputs = []
    collision_rates = []
    waiting_times = []
    utilizations = []

    for _ in range(cfg.num_runs):

        # Init Random Number Generator
        # Independent replications: re-initialize each replication with a different RNG seed
        rng_ = rng.RandomNumberGenerator()
        # Alternative: initialize with fixed seed in order to ensure reproducibility of the simulation
        # rng_ = rng.RandomNumberGenerator(cfg.seed)

        # Only for debug purposes
        if (_ + 1) % 100 == 0:
            logger.debug("[CSMA]  :: Run number %d" % (_ + 1))

        # Generate rvs for each station in the simulated model for the three different categories
        # TODO: define upper and lower interval bound using the config file
        packet_probs = [rng_.generate_random_uniform(0.05, 0.2) for _ in range(num_stations)]
        transmission_times = [rng_.generate_random_int(1, 3) for _ in range(num_stations)]
        packet_sizes = [rng_.generate_random_int(50, 1500) for _ in range(num_stations)]

        tput, c_rate, _, _, w_time, coll = sim_csma(num_stations, cfg, packet_probs, transmission_times,
                                              packet_sizes, rng_, logger)

        throughputs.append(tput)
        collision_rates.append(c_rate)
        waiting_times.append(w_time)

    return {
        "throughput": throughputs,
        "collision_rate": collision_rates,
        "delay": waiting_times,
        "lost_packets": None,
        "tx_packets": None
    }


def main():

    # Run simulations from the method defined in simulation.py
    simulations.start_simulations(['csma'])


if __name__ == "__main__":
    main()
