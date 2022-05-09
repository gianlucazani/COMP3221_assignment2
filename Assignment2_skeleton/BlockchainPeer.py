import time
from BlockchainMiner import BlockchainMiner
from BlockchainServer import BlockchainServer
from BlockchainClient import BlockchainClient
import sys

GENESIS_BLOCK_PROOF = 100


class BlockchainPeer:
    def __init__(self):
        # initialise variables from the command line input
        self.node_id = sys.argv[1]
        self.port_no = int(sys.argv[2])
        self.config_fp = sys.argv[3]
        self.port_dict = {}
        self.node_timeouts = {}

        f = open(self.config_fp, 'r')
        self.num_adj_nodes = int(f.readline())

        for i in range(self.num_adj_nodes):
            _input = f.readline()
            _input = _input.split()
            self.port_dict[_input[0]] = int(_input[1])
            self.node_timeouts.update({_input[0]: {'ping': time.time(), 'state': True}})

    def run(self):
        blockchain_server_thread = BlockchainServer(self.node_id, self.port_no, self.node_timeouts,
                                                    self.port_dict, GENESIS_BLOCK_PROOF)
        blockchain_miner_thread = BlockchainMiner(self.port_no)
        blockchain_client_thread = BlockchainClient(self.port_no, self.port_dict)
        blockchain_server_thread.start()
        blockchain_miner_thread.start()
        blockchain_client_thread.start()
        while blockchain_client_thread.alive and blockchain_miner_thread.alive and blockchain_server_thread.alive:
            pass
        return


peer = BlockchainPeer()
peer.run()
print(f"Peer terminated successfully")
sys.exit(0)
