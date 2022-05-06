import time
from BlockchainMiner import BlockchainMiner
from BlockchainServer import BlockchainServer
from BlockchainClient import BlockchainClient
import sys



GENESIS_BLOCK_PROOF = 100
class BlockchainPeer():
    def __init__(self, *args):
        # initialise variables from the command line input
        self.node_id = sys.argv[1]
        self.port_no = int(sys.argv[2])
        self.config_fp = sys.argv[3]
        self.port_dict = {}
        self.node_timeouts = {}

        f = open(self.config_fp, 'r')
        self.num_adj_nodes = int(f.readline())

        self.nodes = []

        for i in range(self.num_adj_nodes):
            input = f.readline()
            input = input.split()
            self.nodes.append(input[0])
            self.port_dict[input[0]] = int(input[1])
            self.node_timeouts.update({input[0]: {'ping': time.time(), 'state': True}})

    def run(self):
        blockchain_server_thread = BlockchainServer(self.node_id, self.port_no, self.node_timeouts, self.nodes, self.port_dict, GENESIS_BLOCK_PROOF)
        blockchain_miner_thread = BlockchainMiner(int(self.port_no)+2, self.port_no)
        blockchain_client_thread = BlockchainClient(int(self.port_no)+4, self.port_no)
        blockchain_server_thread.start()
        # blockchain_miner_thread.start()
        blockchain_client_thread.start()

peer = BlockchainPeer()
peer.run()
