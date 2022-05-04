import time
from lib import calculate_hash


class Block:
    def __init__(self, index: int, transactions: list, proof: int, previous_hash: str, current_hash=None):
        """
        Creates a new Block object
        :param index: index of the block in the blockchain
        :param transactions: list of Transaction objects
        :param proof: integer, represents the nonce
        :param previous_hash: string representing the reference to the previous block in the blockchain (is the previous block's current_hash)
        :param current_hash: optional value (default None), if kept at its default, the block will automatically compute its hash starting from its content. If a value is passed, then the current_hash of the block will be the passed value
        """
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.proof = proof  # it is the nonce
        self.previous_hash = previous_hash  # previous block's current_hash
        if current_hash is not None:
            self.current_hash = current_hash
        else:
            self.get_current_hash()

    def get_current_hash(self):
        """
        Calculates the current_hash of the block from its content
        """
        content_to_hash = ""
        content_to_hash += str(self.index)
        # We do not hash the timestamp because when the genesis block is created, it is created at slightly (or big) different times by the peers
        # and if we hash the timestamp, we will end up having all different genesis blocks (and so genesis blocks' current hashes)
        # content_to_hash += str(self.timestamp)
        content_to_hash += str(self.proof)
        content_to_hash += self.previous_hash
        for transaction in self.transactions:
            content_to_hash += transaction.get_as_string()  # will get the transaction in the string format tx|sender|content
        self.current_hash = calculate_hash(content_to_hash)
