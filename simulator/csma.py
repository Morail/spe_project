import utils
import simulations
import rng
import stats
import channel
from station import CsmaStation


def sim_csma(num_stations, cfg, packet_probs, packet_sizes, rng_, logger):
    successful_transmissions = 0
    total_transmissions = 0
    collisions = 0

    c = channel.Channel()
    stations = [CsmaStation(i, packet_probs[i], packet_sizes[i], rng_, cfg.max_backoff_time) for i in range(num_stations)]

    # Time advances with fixed increments
    for epoch in range(cfg.num_epochs):

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

        sender = None
        # Iterate over all the stations in TX=transmit state
        for txs in transmitting:
            txs.start_tx()

            # Sense the channel first
            if not c.is_busy:
                # first come, first serve
                # Channel is free, start transmission
                c.transmit(epoch, txs.packet_size)
                # Set sender
                sender = txs

            else:
                # Transmitting station waits a random time before trying once again
                txs.wait()

        # Deliver the packet, free the channel
        # This update the statistics
        c.deliver()
        if sender is not None:
            # Ack the sender
            sender.get_ack()

        # Decrease waiting time for stations in WAIT state, as a way to
        # simulate the time clock advancing
        # Once waiting time is back to 0 the station will be
        # ready to retransmit the package
        for w in waiting:
            w.decrease_waiting_time()

    # Compute statistics Throughput: Track successful transmissions and their packet sizes. Calculate the total
    # number of bits transmitted per unit time.
    # TODO: throughput in Mbs
    throughput = c.transmission_size / cfg.num_epochs
    # Successful Transmissions: number of packets successfully transmitted and delivered.
    successful_tx = c.packets
    # Packet Delay: track the time a packet is generated until it's successfully received, considering
    # retransmissions and backoff delays. Average delay across all packets.
    delay = stats.compute_mean([s.waiting_time for s in stations])
    # TODO: Channel Utilization: channel busy time (excluding collisions and backoff periods) and divide it by the total simulation time.
    # TODO: Carrier Sense Time: time stations spend sensing the channel before transmitting. Average carrier all transmission attempts.
    
    return throughput, successful_tx, delay


def run_simulations(num_stations, cfg, logger):
    logger.info("[CSMA]  :: Running %d simulations with %d stations" % (cfg.num_runs, num_stations))

    throughput = []
    delays = []
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
        packet_sizes = [rng_.generate_random_int(1, 3) for _ in range(num_stations)]

        tput, tx_pack, delay = sim_csma(num_stations, cfg, packet_probs,
                                                          packet_sizes, rng_, logger)

        # Update simulation's sampled data
        throughput.append(tput)
        tx_packets.append(tx_pack)
        delays.append(delay)

    return {
        "throughput": throughput
        # ,"collision_rate": None
        , "delay": delays
        # , "lost_packets": None
        ,"tx_packets": tx_packets
    }


def main():

    # Run simulations from the method defined in simulation.py
    simulations.start_simulations(['csma'])


if __name__ == "__main__":
    main()
