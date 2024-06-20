import utils
import simulations
import rng
import stats
import channel
from station import CsmaStation


def sim_csma(num_stations, cfg, packet_probs, transmission_times, packet_sizes, rng_, logger):
    successful_transmissions = 0
    total_transmissions = 0
    total_data_transmitted = 0
    channel_time_remaining = 0
    collisions = 0

    c = channel.Channel()
    stations = [CsmaStation(i, packet_probs[i], packet_sizes[i], rng_, cfg.max_backoff_time) for i in range(num_stations)]

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

    # Compute statistics Throughput: Track successful transmissions and their packet sizes. Calculate the total
    # number of bits transmitted per unit time.
    # TODO: throughput in Mbs
    throughput = c.transmission_size / cfg.num_epochs
    # Collision Rate: number of collisions during the simulation, divided by the total number of transmission attempts.
    collision_rate = collisions / total_transmissions
    # Successful Transmissions: number of packets successfully transmitted and delivered.
    successful_tx = c.packets
    # Packet Delay: track the time a packet is generated until it's successfully received, considering
    # retransmissions and backoff delays. Average delay across all packets.
    delay = stats.compute_mean([s.waiting_time for s in stations])
    # Lost packets: number of packets lost due to maximum backoff excess after a collision and unsuccessful
    # retransmission. Average delay across all packets.
    lost_packets = stats.compute_mean([s.lost_packets for s in stations])
    # Channel Utilization: channel busy time (excluding collisions and backoff periods) and divide it by
    # the total simulation time. - Carrier Sense Time: Track the time stations spend sensing the channel before
    # transmitting. Calculate the average carrier sense time across all transmission attempts.
    
    return throughput, collision_rate, successful_transmissions, total_transmissions, delay


def run_simulations(num_stations, cfg, logger):
    logger.info("[CSMA]  :: Running %d simulations with %d stations" % (cfg.num_runs, num_stations))

    throughput = []
    collision_rates = []
    delays = []
    lost_packets = []
    tx_packets = []

    for _ in range(cfg.num_runs):

        # Init Random Number Generator
        # Independent replications: re-initialize each replication with a different RNG seed
        # Alternative: initialize with fixed seed in order to ensure reproducibility of the simulation
        if not cfg.seed or cfg.seed is None or cfg.seed == 'None' or cfg.seed == '':
            rng_ = rng.RandomNumberGenerator()
        else:
            rng_ = rng.RandomNumberGenerator(cfg.seed)

        if (_ + 1) % 100 == 0:
            logger.debug("[ALOHA] :: Run number %d" % (_ + 1))

        # Generate rvs for each station in the simulated model for the three different categories
        # TODO: define upper and lower interval bound using the config file
        packet_probs = [rng_.generate_random_uniform(0.05, 0.4) for _ in range(num_stations)]
        transmission_times = [rng_.generate_random_int(1, 3) for _ in range(num_stations)]
        packet_sizes = [rng_.generate_random_int(50, 1500) for _ in range(num_stations)]

        tput, c_rate, tx_pack, delay, l_packs = sim_csma(num_stations, cfg, packet_probs,
                                                          transmission_times,
                                                          packet_sizes, rng_, logger)

        # Update simulation's sampled data
        throughput.append(tput)
        collision_rates.append(c_rate)
        delays.append(delay)
        lost_packets.append(l_packs)
        tx_packets.append(tx_pack)

    return {
        "throughput": throughput
        # ,"collision_rate": collision_rates
        , "delay": delays
        , "lost_packets": None
        # ,"tx_packets": None
    }


def main():

    # Run simulations from the method defined in simulation.py
    simulations.start_simulations(['csma'])


if __name__ == "__main__":
    main()
