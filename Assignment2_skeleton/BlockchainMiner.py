import socket
import _thread
import time

from assignment2.lib.lib import calculate_hash

HOST = "127.0.0.1"


class BlockchainMiner:
    def __init__(self, port, server_port):
        self.port = port
        self.server_port = server_port

    def run(self):
        _thread.start_new_thread(self.poll_server())

    def proof_of_work(self, previous_proof):
        new_proof = 0
        while calculate_hash(new_proof ** 2 - previous_proof ** 2)[:2] != "00":
            new_proof += 1
        return new_proof

    def poll_server(self):
        while True:
            time.sleep(1)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # CONNECT TO SERVER
                try:
                    s.connect((HOST, int(self.server_port)))
                except socket.error as e:
                    print(f"Miner {self.port} error CONNECTING with server {self.server_port}")
                    print(f"ERROR {e}")
                    continue

                # REQUEST CURRENT PROOF OWNED BY SERVER
                try:
                    message = "gp"  # message is "get proof" request command to send to the server
                    s.sendall(bytes(message, encoding="utf-8"))
                except socket.error as e:
                    print(f"Miner {self.port} error SENDING REQUEST to server {self.server_port}")
                    print(f"ERROR {e}")
                    continue

                # RECEIVE PROOF FROM SERVER
                # If Miner receives a -1 that means that the server already has a next proof to use for the next block
                # If I receive a positive number, this is the prof from which to compute the next proof
                try:
                    s.listen()  # listen for now messages
                    blockchain_server, address = s.accept()  # accept connection request
                    received = blockchain_server.recv(4096)
                    server_proof = int(received.decode("utf-8"))
                    if server_proof > 0:
                        new_proof = self.proof_of_work(server_proof)
                        message = f"up|{new_proof}"

                        # SEND NEW PROOF TO SERVER
                        try:
                            s.sendall(bytes(message, encoding="utf-8"))
                        except socket.error as e:
                            print(f"Miner {self.port} error SENDING PROOF to server {self.server_port}")
                            print(f"ERROR {e}")
                            continue
                    s.close()
                except socket.error as e:
                    print(f"Miner {self.port} error RECEIVING PROOF to server {self.server_port}")
                    print(f"ERROR {e}")
                    continue

