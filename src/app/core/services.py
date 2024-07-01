import random


def get_random_entry(entries):
    index = random.randint(0, len(entries))
    return entries[index]