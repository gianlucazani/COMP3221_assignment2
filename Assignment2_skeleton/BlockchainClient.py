import _pickle
from _thread import *
import threading
import time
import socket
import _thread
import sys
import json

HOST = "127.0.0.1"


class BlockchainClient(threading.Thread):
    def __init__(self, port_no, server_port_no):
        super().__init__()
        self.port_no = port_no
        self.server_port_no = server_port_no
        self.alive = True

    def run(self):
        while self.alive:
            print("Which action do you want to perform?")
            print("1) Transaction [tx|{sender}|{content}]")
            print("2) Print Blockchain [pb]")
            print("3) Close Connection [cc]")
            choice = input()
            match choice:
                case "tx":
                    self.send_transaction()

                case "pb":
                    print_blockchain_thread = threading.Thread(target=self.print_blockchain)
                    print_blockchain_thread.start()
                case "cc":
                    close_connection_thread = threading.Thread(target=self.close_connection)
                    close_connection_thread.start()

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
                received = s.recv(4096)
                print(received.decode("utf-8"))
            except socket.error as e:
                print(f"Client {self.port_no} error RECEIVING TRANSACTION VALIDATION from server {self.server_port_no}")
                print(f"ERROR {e}")

    def print_blockchain(self):
        """
        Asks the server the blockchain as json and prints it at terminal
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
                print(f"Client {self.port_no} error SENDING PB REQUEST to server {self.server_port_no}")
                print(f"ERROR {e}")

            # RECEIVE BLOCKCHAIN AS JSON FROM SERVER
            try:
                received = s.recv(4096)
                blockchain = _pickle.loads(received)
                print(f"BLOCKCHAIN JSON: \n {blockchain.blockchain_string()}")
            except socket.error as e:
                print(f"Client {self.port_no} error RECEIVING BLOCKCHAIN from server {self.server_port_no}")
                print(f"ERROR {e}")

    def close_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # CONNECT TO SERVER
            try:
                s.connect((HOST, int(self.server_port_no)))
            except socket.error as e:
                print(f"Client {self.port_no} error CONNECTING with server {self.server_port_no}")
                print(f"ERROR {e}")

            # SEND PB REQUEST TO SERVER
            try:
                message = "cc"
                s.sendall(bytes(message, encoding="utf-8"))
            except socket.error as e:
                print(f"Client {self.port_no} error SENDING CC REQUEST to server {self.server_port_no}")
                print(f"ERROR {e}")

            # CLIENT DIES
            self.alive = False

