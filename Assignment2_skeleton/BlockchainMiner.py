import _pickle
import socket
import _thread
import threading
import time

from lib import calculate_hash

HOST = "127.0.0.1"


class Worker(threading.Thread):
    def __init__(self, proof_to_work_on, server_port_no):
        super().__init__()
        self.working_on_proof = proof_to_work_on
        self.server_port_no = server_port_no
        self.running = False

    def run(self):
        while True:
            if not self.running:  # if worker is paused, do nothing
                continue
            next_proof = 0
            # if worker is running (i.e. has to find the next_proof for the server)
            # keep trying finding the next_proof
            # the while loop is blocked from the miner if it gets notified from the server that the proof the worker is working has already been found
            while self.running and calculate_hash(next_proof ** 2 - self.working_on_proof ** 2)[:2] != "00":
                next_proof += 1
            if self.running:  # if you went out of the loop because you found the proof of work (and not because you've been paused)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, int(self.server_port_no)))
                    message = f"up|{next_proof}"

                    # SEND NEW PROOF TO SERVER
                    try:
                        if self.running:  # if at this point you're still running, you can send the next_proof back to the server
                            s.sendall(bytes(message, encoding="utf-8"))
                            self.pause()  # pause myself and wait for the miner to activate me at the next "gp"
                            received = s.recv(4096)
                            print(received.decode("utf-8"))
                    except socket.error as e:
                        print(f"Miner error SENDING PROOF to server {self.server_port_no}")
                        print(f"ERROR {e}")
                        continue

    def pause(self):
        self.running = False

    def activate(self):
        self.running = True


class BlockchainMiner(threading.Thread):
    def __init__(self, server_port_no):
        super().__init__()
        self.server_port_no = server_port_no
        self.prev_proof = 100  # genesis block proof
        # self.work_on_next_proof = True
        self.worker_thread = Worker(self.prev_proof, self.server_port_no)
        self.alive = True

    def run(self):
        self.worker_thread.start()  # will not work on a new proof at the start, will start working for the first time after the first "gp" signal
        poll_server_thread = threading.Thread(target=self.poll_server)
        poll_server_thread.start()

    def poll_server(self):
        dead_server_counter = 0
        while self.alive:
            time.sleep(1)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # CONNECT TO SERVER
                try:
                    s.connect((HOST, int(self.server_port_no)))
                except socket.error as e:
                    dead_server_counter += 1
                    if dead_server_counter > 2:
                        self.alive = False
                        self.worker_thread.pause()
                        exit()
                        raise SystemExit(0)
                    # print(f"Miner {self.port_no} error CONNECTING with server {self.server_port_no}")
                    # print(f"ERROR {e}")
                    continue

                # REQUEST CURRENT PROOF OWNED BY SERVER
                try:
                    message = "gp"  # message is "get proof" request command to send to the server
                    s.sendall(bytes(message, encoding="utf-8"))

                except socket.error as e:
                    print(f"Miner {self.port_no} error SENDING REQUEST to server {self.server_port_no}")
                    print(f"ERROR {e}")
                    continue

                # RECEIVE PROOF FROM SERVER
                try:
                    received = s.recv(4096)
                    proofs_dictionary = _pickle.loads(received)

                    # The package received from the server is in the format { "prev_proof": int, "next_proof": int (-1 if server needs a next proof)}
                    # CASES:
                    # A) prev_proof is the same as worker_thread.working_on_proof
                    # B) prev_proof is different from worker_thread.working_on_proof -> Happens if the server receives a block which has the proof the worker is working on
                    # C) next_proof is a positive integer -> Server has the next proof already
                    # D) next_proof is -1, server needs the next proof

                    if proofs_dictionary["next_proof"] >= 0:  # if C
                        self.worker_thread.pause()  # pause the worker because there's no need to compute the next proof
                        self.worker_thread.working_on_proof = proofs_dictionary["prev_proof"]
                    elif proofs_dictionary["next_proof"] == -1:  # if D
                        print(f"starting on working on a new thread. {proofs_dictionary}")
                        # and the prev_proof if different from the one the worker is working on, make the worker work for the next proof
                        if proofs_dictionary["prev_proof"] != self.worker_thread.working_on_proof:
                            self.worker_thread.pause()  # pause worker
                            self.worker_thread.working_on_proof = proofs_dictionary[
                                "prev_proof"]  # change proof to work on
                            self.worker_thread.activate()  # reactivate worker
                        # if next_proof is -1 and prev_proof is equal to the one the worker is working on, do nothing and let the worker work
                        # at the first poll_server run this is the branch that will be selected and that will activate the Worker for the first time
                        else:
                            self.worker_thread.activate()
                except socket.error as e:
                    print(f"Miner {self.port_no} error RECEIVING PROOF to server {self.server_port_no}")
                    print(f"ERROR {e}")
                    continue
