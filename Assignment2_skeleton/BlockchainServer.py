from multiprocessing import Lock
import threading
import socket
import _pickle
import math
from classes.Blockchain import Blockchain
from classes.Transaction import Transaction
import time

class BlockchainServer():
    def __init__(self, node_id, port_no, node_timeouts, nodes, port_dict):
        self.HOST = "127.0.0.1"
        self.node_id = node_id
        self.port_no = port_no
        self.node_timeouts = node_timeouts
        self.nodes = nodes
        self.port_dict = port_dict
        self.Blockchain = Blockchain()
        self.proof = -1
    
    def run(self):
        self.server =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, int(self.port_no)))
        start_wss_thread = threading.Thread(target=self.start_wss)
        start_wss_thread.start()
        
        print("hi from running")
        pass

    def start_wss(self):
        self.server.listen()
        while True: 
            conn, addr = self.server.accept()
            msg = _pickle.loads(conn.recv(2048))
            match msg[0:2]: 
                case "up":
                    update_proof_thread = threading.Thread(target=self.update_proof, args=(msg,))
                    update_proof_thread.start()
                case "tx":
                    update_transaction_thread = threading.Thread(target=self.update_transaction, args=(msg,))
                    update_transaction_thread.start()
           


    def update_proof(self,msg):
        print("updating proof")

    def update_transaction(self,msg):
        print("validating transaction")
        prev_block = self.Blockchain.get_previous_block()
        msg = msg.split("|")
        transaction = Transaction(msg[1], msg[2])
        if transaction.validate():
            self.Blockchain.add_transaction(transaction)
            if self.Blockchain.pool_length == 5:
                print("success")
                while self.proof == prev_block.proof:
                    time.sleep(1)
        else: 
            print("reject")
