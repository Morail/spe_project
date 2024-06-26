import random
import sys


# TODO: change it to Singleton pattern
class RandomNumberGenerator:
    """
    This class mocks a Random Number Generator by importing the default python random modules.
    The reason behind the choice to implement this class rather than relying on the random module
    is to use the same seed for all the draws.
    """

    def __init__(self, seed=None):
        if seed is None:
            seed = random.SystemRandom().randint(0, sys.maxsize)
        random.seed(seed)

    def generate_random(self):
        return random.random()

    def generate_random_int(self, a, b):
        return random.randint(a, b)

    def generate_random_uniform(self, a, b):
        return random.uniform(a, b)
