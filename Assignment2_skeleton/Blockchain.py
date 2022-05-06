from Block import Block


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
        self.transaction_pool = []
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

    def pool_length(self):
        return len(self.transaction_pool)

    def get_previous_index(self):
        """
        :return: Returns the previous hash (previous block's current hash) as a string
        """
        previous_block = self.get_previous_block()
        return previous_block.index

    def add_transaction(self, transaction):
        """
        adds transaction to the transaction pool
        """
        self.transaction_pool.append(transaction)
        # sort transactions in pool based on timestamp

    def get_previous_proof(self):
        previous_block = self.get_previous_block()
        return previous_block.proof

    def get_five_transactions(self):
        """
        Pops the from the transaction pool the first 5 transactions that have to be added into a new block
        :return: List of transactions as strings in the format tx|sender|content
        """
        first_five_transactions = list()
        for i in range(5):
            # Remove get_as_string if we decide to handle transactions as normal string and not as objects
            first_five_transactions.append(self.transaction_pool.pop(0).get_as_string())
        return first_five_transactions
