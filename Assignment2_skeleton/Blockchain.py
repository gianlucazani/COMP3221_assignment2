import hashlib
import json
from time import time
import datetime

from assignment2.Assignment2_skeleton.Block import Block


class Blockchain:
    def __init__(self):
        self.blockchain = list()  # list of Block objects
        self.transaction_pool = list()  # list of Transaction objects
