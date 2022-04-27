import time


class Block:
    def __init__(self, index, transactions, proof, previous_hash, current_hash):
        self.index = index
        self.timestamp = time.now()
        self.transactions = transactions
        self.proof = proof # it is the nonce
        self.previous_hash = previous_hash # previous block's current_hash
        self.current_hash = current_hash


