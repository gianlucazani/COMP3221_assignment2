from _thread import *
import threading
import time
import socket
import _thread
import sys
import json
import hashlib
import time

from assignment2.lib.lib import calculate_hash

HOST = "127.0.0.1"

class BlockchainMiner:
    def __init__(self, current_proof, port, server_port):
        self.port = port
        self.server_port = server_port
        self.current_proof = current_proof

    def run(self):
        while True:
            time.sleep(1)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((HOST, int(self.server_port)))
                    message = "gp"  # message is "get proof" request command to send to the server
                    s.sendall(bytes(message, encoding="utf-8"))
                    s.listen()  # listen for now messages
                    blockchain_server, address = s.accept()  # accept connection request
                    received = blockchain_server.recv(4096)
                    previous_proof = int(received.decode("utf-8"))
                    if previous_proof != self.current_proof:
                        new_proof = self.proof_of_work(previous_proof)
                        message = f"up|{new_proof}"
                        s.sendall(bytes(message, encoding="utf-8"))
                    s.close()
                except Exception as e:
                    print(f"Miner {self.port} ERROR COMMUNICATING WITH SERVER {self.server_port}")
                    continue

    def proof_of_work(self, previous_proof):
        new_proof = 0
        while calculate_hash(new_proof ** 2 - previous_proof ** 2)[:2] != "00":
            new_proof += 1
        self.current_proof = new_proof
        return new_proof
