from multiprocessing import Lock
import re
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
    def __init__(self, server, lock):
        super(Heartbeat, self).__init__()
        self.server = server
        self.blockchain_lock = lock

    def run(self):
        while self.server.alive:
            time.sleep(5)
            for peer_id, destination_port in self.server.port_dict.items():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # SEND HEARTBEAT
                    heartbeat = "hb"
                    try:
                        s.connect((HOST, int(destination_port)))
                        s.sendall(bytes(heartbeat, encoding="utf-8"))
                    except socket.error as e:
                        print(f"Server {self.server.port_no} error SENDING HEARTBEAT to {peer_id}")
                        print(f"ERROR {e}")

                    # LISTEN FOR PEER'S BLOCKCHAIN JSON
                    try:
                        received = s.recv(4096)
                        received_blockchain_json = received
                    except socket.error as e:
                        print(f"Server {self.server.port_no} error RECEIVING BLOCKCHAIN JSON in HB from {destination_port}")
                        print(f"ERROR {e}")
                        continue

                    if received_blockchain_json:
                        self.blockchain_lock.acquire()
                        self.compare_blockchains(received_blockchain_json)
                        self.blockchain_lock.release()

    def compare_blockchains(self, other_blockchain_json):
        """
        This method will:
        1) Compare the received blockchain's length with ours
        2) If the length is greater, it checks if all the exceeding blocks are valid (valid transactions inside)
        3) If so, it will update the blockchain with the new, longer one
        :param other_blockchain_json: received json from server after hb
        """
        other_blockchain = _pickle.loads(other_blockchain_json)
        if isinstance(other_blockchain,
                      Blockchain):  # if the thing the peer sent me is actually a Blockchain object, then I can comapre it
            if len(other_blockchain.blockchain) > len(self.server.Blockchain.blockchain):  # check chains lengths
                exceeding_blocks = self.get_exceeding_blocks(other_blockchain)
                if self.valid_exceeding_blocks(exceeding_blocks):
                    self.update_blockchain(other_blockchain)  # keep the longest chain

    def get_exceeding_blocks(self, other_blockchain: Blockchain):
        """
        Returns a list of blocks that are the ones existing in the received blockchain but not in ours
        :param other_blockchain: received Blockchain object
        :return: list(Block)
        """
        length_difference = len(other_blockchain.blockchain) - len(self.server.Blockchain.blockchain)
        exceeding_blocks = other_blockchain.blockchain[-length_difference:]
        return exceeding_blocks

    def valid_exceeding_blocks(self, exceeding_blocks):
        """
        Checks that each exceeding block is valid (all the transactions inside are valid)
        :param exceeding_blocks: list(Block)
        :return: True if all valid, False otherwise
        """
        for block in exceeding_blocks:
            print(f"block from validate exceeding blocks {block}")
            if not block.is_valid():
                return False
        return True

    def update_blockchain(self, new_blockchain: Blockchain):
        """
        Updates our blockchain with the received one, updates server's known prev_proof and next_proof
        It will update also the transaction pool
        :param new_blockchain: Blockchain object
        """
        self.server.Blockchain = new_blockchain
        self.server.prev_proof = self.server.Blockchain.get_previous_proof()
        self.server.next_proof = -1


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
        self.blockchain_lock = Lock()
        self.alive = True

    def run(self):
        self.heartbeat_thread = Heartbeat(self, self.blockchain_lock)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, int(self.port_no)))
        start_wss_thread = threading.Thread(target=self.start_wss)
        start_wss_thread.start()
        self.heartbeat_thread.start()

    def start_wss(self):
        try:
            self.server.listen()
            while self.alive:
                conn, address = self.server.accept()
                msg = (conn.recv(2048)).decode("utf-8")
                match msg[0:2]:
                    case "gp":
                        get_proof_thread = threading.Thread(target=self.get_proof, args=(conn,))
                        get_proof_thread.start()
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
                    case "cc":
                        self.server.close()
                        self.alive = False
                        exit()
                        raise SystemExit(0)
        except socket.error as e:
            print(f"Server {self.port_no} error RECEIVING from port {address}")
            print(f"ERROR {e}")

    def get_proof(self, conn):
        payload = {
            "prev_proof": self.Blockchain.get_previous_proof(),
            "next_proof": self.next_proof
        }
        conn.sendall(_pickle.dumps(payload))

    def update_proof(self, msg, conn):
        proof = int(msg[3:])

        # validate proof is correct
        print(f"prev proof from server is: {self.prev_proof}")
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
        blockchain_json = _pickle.dumps(self.Blockchain, )
        conn.sendall(blockchain_json)

    def create_block(self):
        if self.Blockchain.pool_length() >= 5 and self.next_proof > 0:
            transactions = self.Blockchain.get_five_transactions()
            self.blockchain_lock.acquire()
            block = Block(self.Blockchain.get_previous_index() + 1, transactions, self.next_proof,
                          self.Blockchain.get_previous_block_hash())
            self.Blockchain.add_new_block(block)
            self.blockchain_lock.release()
            self.prev_proof = self.next_proof
            self.next_proof = -1
