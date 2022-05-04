from multiprocessing import Lock
import threading
import socket
import _pickle
import math
from classes.Blockchain import Blockchain
from classes.Transaction import Transaction
import time

HOST = "127.0.0.1"


class BlockchainServer:
    def __init__(self, node_id, port_no, node_timeouts, nodes, port_dict, genesis_block_proof):
        self.node_id = node_id
        self.port_no = port_no
        self.node_timeouts = node_timeouts
        self.nodes = nodes
        self.port_dict = port_dict
        self.Blockchain = Blockchain()
        self.next_proof = -1
        self.prev_proof = genesis_block_proof

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, int(self.port_no)))
        start_wss_thread = threading.Thread(target=self.start_wss)
        start_wss_thread.start()

        print("hi from running")
        pass

    def start_wss(self):
        try:
            self.server.listen()
            while True:
                conn, address = self.server.accept()
                msg = _pickle.loads(conn.recv(2048))
                match msg[0:2]:
                    case "up":
                        update_proof_thread = threading.Thread(target=self.update_proof, args=(msg,))
                        update_proof_thread.start()
                    case "tx":
                        update_transaction_thread = threading.Thread(target=self.update_transaction, args=(msg,))
                        update_transaction_thread.start()
        except socket.error as e:
            print(f"Server {self.port_no} error RECEIVING from port {address}")
            print(f"ERROR {e}")

    def update_proof(self, msg):
        print("updating proof")

    def update_transaction(self, msg):
        print(f"Server {self.port_no} is validating transaction")
        prev_block = self.Blockchain.get_previous_block()
        msg = msg.split("|")
        if len(msg) == 3:
            transaction = Transaction(msg[1], msg[2])
            if transaction.validate():
                # server sends an "Accepted" message to client
                self.Blockchain.add_transaction(transaction)
                if self.Blockchain.pool_length >= 5:
                    self.create_block()
            else: 
                # server sends "Rejected" message to client
                print("reject")
        else:
            # server sends "Rejected" message to client
            print("reject")
    
    def create_block(self):
        if self.Blockchain.pool_length >= 5 and self.next_proof > 0:
            self.prev_proof = self.next_proof
            self.next_proof = -1
            transactions = self.Blockchain.get_five_transactions()
            
