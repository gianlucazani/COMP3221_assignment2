from classes.Block import Block


class Blockchain:
    def __init__(self):
        """
        Creates the blockchain and adds the genesis block
        """
        self.blockchain = list()  # list of Block objects
        self.transaction_pool = list()  # list of Transaction objects

        genesis_block = Block(1, self.transaction_pool, 100, "This block has no previous hash")
        self.add_new_block(genesis_block)

    def add_new_block(self, block: Block):
        """
        Adds the new Block to the blockchain
        :param block: Block object to be added
        """
        self.blockchain.append(block)

    def get_previous_block(self):
        """
        :return: Last Block in the blockchain as Block object
        """
        return self.blockchain[-1]

    def get_previous_block_hash(self):
        """
        :return: Returns the previous hash (previous block's current hash) as a string
        """
        previous_block = self.get_previous_block()
        return previous_block.current_hash


