from channel import Channel
from station import AlohaStation

import simulations
import stats
import rng


def sim_aloha(num_stations, cfg, packet_probs, packet_sizes, rng_, logger):
    total_transmissions = 0
    collisions = 0

    # Instance of a new channel
    channel = Channel()
    # Init stations
    stations = [AlohaStation(i, packet_probs[i], packet_sizes[i], rng_, cfg.max_backoff_time) for i in range(num_stations)]

    # Time advances with fixed increments
    for epoch in range(cfg.num_epochs):

        # Only for debug purposes
        if (epoch + 1) % 1000 == 0:
            logger.debug(("Processing %d epoch" % (epoch + 1)))

        # List of stations ready to transmit a frame
        transmitting = [s for s in stations if s.has_frame_to_transmit()]

        # List of nodes waiting for the backoff time to be over
        waiting = [s for s in stations if s.is_waiting()]

        # Keep count of total transmission
        total_transmissions += len(transmitting)

        # Check if there are nodes ready to transmit
        if not transmitting:
            # No nodes ready to start a transmission
            continue

        # Iterate over all the stations in TX=transmit state
        for txs in transmitting:
            txs.start_tx()
            # Start transmission
            channel.transmit(epoch, txs.packet_size)

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
            logger.debug("Slot %d : collision detected between %d nodes" % (epoch + 1, len(transmitting)))
            logger.debug('Colliding nodes: %s' % ', '.join(str(t) for t in transmitting))

            # In case of collision sent packets are lost
            for txs in transmitting:
                # Increment the collisions' counter by the number of transmitting nodes
                collisions += len(transmitting)
                # Sending station has to handle with the collision
                txs.handle_collision()

        # Decrease waiting time for stations in WAIT state, as a way to
        # simulate the time clock advancing
        # Once waiting time is back to 0 the station will be
        # ready to retransmit the package
        for w in waiting:
            w.decrease_waiting_time()

    # Compute statistics Throughput: Track successful transmissions and their packet sizes. Calculate the total
    # number of bits transmitted per unit time.
    # TODO: throughput in Mbs
    throughput = channel.transmission_size / cfg.num_epochs
    # Collision Rate: number of collisions during the simulation, divided by the total number of transmission attempts.
    collision_rate = collisions / total_transmissions
    # Successful Transmissions: number of packets successfully transmitted and delivered.
    successful_tx = channel.packets
    # Packet Delay: track the time a packet is generated until it's successfully received, considering
    # retransmissions and backoff delays. Average delay across all packets.
    delay = stats.compute_mean([s.waiting_time for s in stations])
    # Lost packets: number of packets lost due to maximum backoff exceedence after a collision and unsuccessful
    # retransmission. Average delay across all packets.
    lost_packets = stats.compute_mean([s.lost_packets for s in stations])

    return throughput, collision_rate, successful_tx, delay, lost_packets


def run_simulations(num_stations, cfg, logger):
    logger.info("[ALOHA] :: Running %d simulations with %d stations" % (cfg.num_runs, num_stations))

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
        packet_probs = [rng_.generate_random_uniform(0.05, 0.2) for _ in range(num_stations)]
        packet_sizes = [rng_.generate_random_int(1, 3) for _ in range(num_stations)]

        tput, c_rate, tx_pack, delay, l_packs = sim_aloha(num_stations, cfg, packet_probs,
                                                          packet_sizes, rng_, logger)

        # Update simulation's sampled data
        throughput.append(tput)
        collision_rates.append(c_rate)
        delays.append(delay)
        lost_packets.append(l_packs)
        tx_packets.append(tx_pack)

    return {
        "throughput": throughput
        , "collision_rate": collision_rates
        , "delay": delays
        , "lost_packets": lost_packets
        , "tx_packets": tx_packets
    }


def main():
    # Run simulations from the method defined in simulation.py
    simulations.start_simulations(['aloha'])


if __name__ == "__main__":
    main()
