#!/usr/bin/python3

import random
import string

def generate_key(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))