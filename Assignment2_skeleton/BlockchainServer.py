from multiprocessing import Lock
import threading
import socket
import _pickle
import math
from classes.Blockchain import Blockchain
from classes.Transaction import Transaction

class BlockchainServer():
    def __init__(self, node_id, port_no, node_timeouts, nodes, port_dict):
        self.HOST = "127.0.0.1"
        self.node_id = node_id
        self.port_no = port_no
        self.node_timeouts = node_timeouts
        self.nodes = nodes
        self.port_dict = port_dict
        self.Blockchain = Blockchain()
    
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
                    self.update_proof(msg) 
                case "tx":
                    self.validate_transaction(msg)
            handle_client_thread = threading.Thread(target=self.handle_client, args=(conn, ))
            handle_client_thread.start()


    def update_proof(self,msg):
        print("updating proof")

    def validate_transaction(self,msg):
        print("validating transaction")
        msg = msg.split("|")
        transaction = Transaction(msg[1], msg[2])
        if transaction.validate():
            print("success")
        else: 
            print("reject")
