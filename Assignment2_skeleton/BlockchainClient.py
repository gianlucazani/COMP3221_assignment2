from _thread import *
import threading
import time
import socket
import _thread
import sys
import json

HOST = "127.0.0.1"


class BlockchainClient:
    def __init__(self, port, server_port):
        self.port = port
        self.server_port = server_port

    def run(self):
        while True:
            print("Which action do you want to perform?")
            print("1) Transaction [tx|{sender}|{content}]")
            print("2) Print Blockchain [pb]")
            print("3) Close Connection [cc]")
            print("4) Heartbeat [hb]")
            choice = input()
            if choice == "1":
                _thread.start_new_thread(self.send_transaction())

    def send_transaction(self):
        print("Write the transaction in the format tx|{sender}|{content}")
        transaction = input()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, int(self.server_port)))
                s.sendall(bytes(transaction, encoding="utf-8"))
                s.listen()  # listen for now messages
                blockchain_server, address = s.accept()  # accept connection request
                received = blockchain_server.recv(4096)
                print(received.decode("utf-8"))
            except Exception as e:
                print(f"Client {self.port} ERROR COMMUNICATING WITH SERVER {self.server_port}")

