class Channel:

    def __init__(self, transmission_rate=3 * pow(10, 8)):
        self.is_busy = False
        self.transmission_size = 0
        self.packets = 0
        self.packets_delivered = 0
        self.transmission_rate = transmission_rate  # Channel transmission rate
        self.transmission_time = 0
        self.collision = 0

    def transmit(self, current_time, packet_size):
        self.is_busy = True
        self.packets += 1
        self.transmission_size += packet_size
        # self.transmission_time = packet_size / self.transmission_rate
        self.transmission_time = current_time + packet_size

    def handle_collision(self):
        self.is_busy = False
        self.transmission_time = 0
        self.collision += 1

    def deliver(self):
        self.is_busy = False
        self.packets_delivered += 1

    def set_busy(self, is_busy=True):
        self.is_busy = is_busy
