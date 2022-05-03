from _thread import *
import threading
import time
import socket
import _thread
import sys
import json

HOST = "127.0.0.1"


class BlockchainClient:
    def __init__(self, port_no, server_port_no):
        self.port_no = port_no
        self.server_port_no = server_port_no
        self.blockchain_json = ""

    def run(self):
        _thread.start_new_thread(self.heartbeat())
        while True:
            print("Which action do you want to perform?")
            print("1) Transaction [tx|{sender}|{content}]")
            print("2) Print Blockchain [pb]")
            print("3) Close Connection [cc]")
            choice = input()
            match choice:
                case "1":
                    _thread.start_new_thread(self.send_transaction())
                case "2":
                    _thread.start_new_thread(self.print_blockchain())
                    print(f"Blockchain JSON: {self.blockchain_json}")
                case "3":
                    _thread.start_new_thread(self.close_connection())

    def send_transaction(self):
        print("Write the transaction in the format tx|{sender}|{content}")
        transaction = input()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            # CONNECT TO SERVER
            try:
                s.connect((HOST, int(self.server_port_no)))
            except socket.error as e:
                print(f"Client {self.port_no} error CONNECTING with server {self.server_port_no}")
                print(f"ERROR {e}")

            # SEND TRANSACTION TO SERVER
            try:
                s.sendall(bytes(transaction, encoding="utf-8"))
            except socket.error as e:
                print(f"Client {self.port_no} error SENDING TRANSACTION to server {self.server_port_no}")
                print(f"ERROR {e}")

            # PRINT RESPONSE FROM SERVER ABOUT VALID TRANSACTION
            try:
                s.listen()  # listen for now messages
                blockchain_server, address = s.accept()  # accept connection request
                received = blockchain_server.recv(4096)
                print(received.decode("utf-8"))
            except socket.error as e:
                print(f"Client {self.port_no} error RECEIVING TRANSACTION VALIDATION from server {self.server_port_no}")
                print(f"ERROR {e}")

    def print_blockchain(self):
        """
        Saves into self.blockchain_json the blockchain as a json string
        The methods saves the blockchain in a class attribute because it is hard to collect it as a return value
        after the method is being run by a thread. By saving the value in an attribute it is easier to check differences
        with other blockchains in the heartbeat process. Moreover, by saving it in an attribute we can use the value
        as we want (print it, compare, check values inside, ecc...)
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # CONNECT TO SERVER
            try:
                s.connect((HOST, int(self.server_port_no)))
            except socket.error as e:
                print(f"Client {self.port_no} error CONNECTING with server {self.server_port_no}")
                print(f"ERROR {e}")

            # SEND PB REQUEST TO SERVER
            try:
                message = "pb"
                s.sendall(bytes(message, encoding="utf-8"))
            except socket.error as e:
                print(f"Client {self.port_no} error SENDING REQUEST to server {self.server_port_no}")
                print(f"ERROR {e}")

            # RECEIVE BLOCKCHAIN AS JSON FROM SERVER
            try:
                s.listen()  # listen for now messages
                blockchain_server, address = s.accept()  # accept connection request
                received = blockchain_server.recv(4096)
                blockchain_json = received.decode("utf-8")
                self.blockchain_json = blockchain_json
            except socket.error as e:
                print(f"Client {self.port_no} error RECEIVING BLOCKCHAIN from server {self.server_port_no}")
                print(f"ERROR {e}")

    def close_connection(self):
        pass

    def heartbeat(self):
        while True:
            time.sleep(5)
            # send heartbeat to all the peers
            # collect peers' blockchains (as json)
            # request blockchain to my server (json)
            # compare all blockchains and keep the longest
            # update blockchain
            # HERE IS THE PROBLEM: how to update the blockchain if the server is the only one that can operate on the blockchain?
            # Do we add another command for sending back to my server the updated blockchain (better for synchronization, otherwise the blockchain lock should be shared across server and client)
            # Do we make the blockchain accessible from the client (much more easy but hard to synchronize)
            # ----
            # SOLUTION -> The heartbeat is job of the server, not of the client
            pass

