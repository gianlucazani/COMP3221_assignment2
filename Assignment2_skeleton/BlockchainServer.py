from multiprocessing import Lock
import threading
import socket
import _pickle
import math
from Blockchain import Blockchain
from Transaction import Transaction
import time
from Block import Block
from lib import calculate_hash

HOST = "127.0.0.1"


class Heartbeat(threading.Thread):
    def __init__(self, port_no: int, blockchain: Blockchain, port_dict: dict):
        super(Heartbeat, self).__init__()
        self.port_no = port_no
        self.blockchain = blockchain
        self.port_dict = port_dict

    def run(self):
        while True:
            time.sleep(5)
            for peer_id, destination_port in self.port_dict.items():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # SEND HEARTBEAT
                    heartbeat = "hb"
                    try:
                        s.connect((HOST, int(destination_port)))
                        s.sendall(bytes(heartbeat, encoding="utf-8"))
                    except socket.error as e:
                        print(f"Server {self.port_no} error SENDING HEARTBEAT to {peer_id}")
                        print(f"ERROR {e}")

                    # LISTEN FOR PEER'S BLOCKCHAIN JSON
                    try:
                        received = s.recv(4096)
                        received_blockchain_json = received
                    except socket.error as e:
                        print(f"Server {self.port_no} error RECEIVING BLOCKCHAIN JSON in HB from {destination_port}")
                        print(f"ERROR {e}")
                        continue

                    if received_blockchain_json:
                        # HELLO GEN!! ACQUIRE LOCK HERE <--------------------------------------------------------------------
                        self.compare_blockchains(received_blockchain_json)
                        # RELEASE LOCK HERE

    def compare_blockchains(self, other_blockchain_json: str):
        other_blockchain = _pickle.loads(other_blockchain_json)
        print(other_blockchain)
        if isinstance(other_blockchain,
                      Blockchain):  # if the thing the peer sent me is actually a Blockchain object, then I can comapre it
            if len(other_blockchain.blockchain) > len(self.blockchain.blockchain):  # check chains lengths
                self.update_blockchain(other_blockchain)  # keep the longest chain

    def update_blockchain(self, new_blockchain):
        self.blockchain = new_blockchain


class BlockchainServer(threading.Thread):
    def __init__(self, node_id: int, port_no: int, node_timeouts, nodes, port_dict, genesis_block_proof: int):
        super().__init__()
        self.node_id = node_id
        self.port_no = port_no
        self.node_timeouts = node_timeouts
        self.nodes = nodes
        self.port_dict = port_dict
        self.Blockchain = Blockchain()
        self.next_proof = -1
        self.prev_proof = genesis_block_proof
        self.heartbeat_thread = Heartbeat(port_no, self.Blockchain, port_dict)

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, int(self.port_no)))
        start_wss_thread = threading.Thread(target=self.start_wss)
        start_wss_thread.start()
        self.heartbeat_thread.start()

    def start_wss(self):
        try:
            self.server.listen()
            while True:
                conn, address = self.server.accept()
                msg = (conn.recv(2048)).decode("utf-8")
                match msg[0:2]:
                    case "up":
                        update_proof_thread = threading.Thread(target=self.update_proof, args=(msg, conn))
                        update_proof_thread.start()
                    case "tx":
                        update_transaction_thread = threading.Thread(target=self.update_transaction, args=(msg, conn))
                        update_transaction_thread.start()
                    case "hb":
                        return_heartbeat_thread = threading.Thread(target=self.return_heartbeat, args=(msg, conn))
                        return_heartbeat_thread.start()
                    case "pb":
                        print_blockchain_thread = threading.Thread(target=self.print_blockchain, args=(msg, conn))
                        print_blockchain_thread.start()
        except socket.error as e:
            print(f"Server {self.port_no} error RECEIVING from port {address}")
            print(f"ERROR {e}")

    def update_proof(self, msg, conn):
        proof = int(msg[3:])

        # validate proof is correct
        if calculate_hash(proof ** 2 - self.prev_proof ** 2)[:2] == "00":
            conn.sendall(b"Reward")
            self.next_proof = proof
            self.create_block()
        else:
            conn.sendall(b"No Reward")

    def update_transaction(self, msg, conn):
        print(f"Server {self.port_no} is validating transaction")
        try:
            msg = msg.split("|")
            if len(msg) == 3:
                transaction = Transaction(msg[1], msg[2])
                try:
                    if transaction.validate():
                        conn.sendall(b"Accepted")
                        self.Blockchain.add_transaction(transaction)
                        if self.Blockchain.pool_length() >= 5:
                            self.create_block()
                    else:
                        conn.sendall(b"Rejected")
                except socket.error as e:
                    print(f"Server {self.port_no} error SENDING transaction validation to {conn}")
                    print(f"ERROR {e}")
            else:
                # server sends "Rejected" message to client
                conn.sendall(b"Rejected")
                print("reject")
        except Exception as e:
            print(e)

    def return_heartbeat(self, msg, conn):
        blockchain_json = _pickle.dumps(self.Blockchain)
        conn.sendall(blockchain_json)

    def print_blockchain(self, msg, conn):
        blockchain_json = _pickle.dumps(self.Blockchain)
        conn.sendall(blockchain_json)

    def create_block(self):
        if self.Blockchain.pool_length() >= 5 and self.next_proof > 0:
            transactions = self.Blockchain.get_five_transactions()
            # need to add a lock here
            block = Block(self.Blockchain.get_previous_index() + 1, transactions, self.next_proof,
                          self.Blockchain.get_previous_block_hash())
            self.Blockchain.add_new_block(block)
            # release lock
            self.prev_proof = self.next_proof
            self.next_proof = -1
