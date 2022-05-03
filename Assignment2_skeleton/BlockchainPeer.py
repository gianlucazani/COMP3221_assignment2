import time
from BlockchainServer import BlockchainServer
import sys


class BlockchainPeer():
    def __init__(self, *args):
        # initialise variables from the command line input
        self.node_id = sys.argv[1]
        self.port_no = sys.argv[2]
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
            self.port_dict[input[0]] = input[1]
            self.node_timeouts.update({input[0]: {'ping': time.time(), 'state': True}})

    def run(self):
        server = BlockchainServer(self.node_id, self.port_no, self.node_timeouts, self.nodes, self.port_dict).run()


peer = BlockchainPeer()
peer.run()
