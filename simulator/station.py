import random


class Station:
    # List possible states
    IDLE = 0  # Initial state, station is idle
    TX = 1  # Transmitting
    RTX = 2  # Need to retransmit data due to collision
    WAIT = 3  # waiting backoff time before retransmitting

    # Initialize the stations.
    def __init__(self, id_, packet_prob, packet_size, rng_, max_backoff_time=64):
        self.id = id_
        self.packet_prob = packet_prob
        self.packet_size = packet_size
        self.max_backoff_time = max_backoff_time
        self.rng = rng_

        # Statistics
        self.total_packets = 0
        self.sent_packets = 0
        self.collision = 0
        self.lost_packets = 0
        self.waiting_time = 0
        self.packet_attempt = 0

        # Initial state is IDLE
        self.state = Station.IDLE
        self.backoff_time = 0
        self.packet_attempt = 0

    def set_idle(self):
        self.state = Station.IDLE
        # Reset backoff time
        self.backoff_time = 0
        # Reset the number of total attempts per package
        self.packet_attempt = 0

    def get_ack(self):
        # Increment number of successfully sent packets
        self.sent_packets += 1
        self.set_idle()

    def is_waiting(self):
        return self.state == Station.WAIT

    def decrease_waiting_time(self):
        # Time passes, decreases the value of the
        # backoff time
        self.backoff_time -= 1

        # if backoff time is exhausted, and thus the chosen frame
        # for resending the packet has come, the station enters in the
        # RTX state (ready to re-transmit)
        if not self.backoff_time:
            self.state = Station.RTX

    def has_frame_to_transmit(self):
        # If a station is IDLE then it has a frame to be transmitted with
        # probability equals to the one assigned to the node in the init phase
        # A node in the RXT state has to send data
        return self.state == Station.RTX or (self.state == Station.IDLE and self.rng.generate_random() < self.packet_prob)

    def start_tx(self):
        # Increase the counter holding the total number of packets
        # either delivered or collided
        self.total_packets += 1
        # Increase the number of total attempts
        self.packet_attempt += 1
        # Set state to transmitting
        self.state = Station.TX

    def __repr__(self):
        return "Node [%s]" % self.id


class AlohaStation(Station):

    def __init__(self, id_, packet_prob, packet_size, rng_, max_backoff_time=64):
        super().__init__(id_, packet_prob, packet_size, rng_, max_backoff_time)

    def handle_collision(self):
        self.collision += 1
        self.state = Station.WAIT
        # Random exponential backoff time
        # A station choose, with equal probability, one of the next 2^n frames
        # for sending the packet again, where n is the number of attempt until now
        self.backoff_time = self.rng.generate_random_int(0, (2 ** self.packet_attempt) - 1)

        # if backoff time is 0 the station enters the
        # RTX state (ready to re-transmit)
        if not self.backoff_time:
            self.state = Station.RTX
        # Check whether the max backoff time is respected
        elif self.backoff_time > self.max_backoff_time:
            # Maximum backoff time exceeded, packet shall be dropped
            # and the station return IDLE, resetting the statistics linked
            # to the current packet
            self.lost_packets += 1
            self.set_idle()
        else:
            self.waiting_time += self.backoff_time


class CsmaStation(Station):

    def __init__(self, id_, packet_prob, packet_size, rng_, max_backoff_time=64):
        super().__init__(id_, packet_prob, packet_size, rng_, max_backoff_time)

    def wait(self):
        self.state = Station.WAIT
        # Set backoff time, which in the CSMA/CA case is the random time the station waits
        # before sensing the channel once again
        self.backoff_time = self.rng.generate_random_int(1, self.max_backoff_time)
        self.waiting_time += self.backoff_time

