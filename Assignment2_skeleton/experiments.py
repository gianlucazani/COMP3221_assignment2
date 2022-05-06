import _pickle
import hashlib
import math
import time
import string
import random

import numpy

# times = list()
# for i in range(20):
#
#     start = time.time()
#     S = 10  # number of characters in the string.
#     # call random.choices() string module to find the string in Uppercase + numeric data.
#     ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
#     content = str(ran)
#     rawHash = hashlib.sha256(content.encode())
#     proof = rawHash.hexdigest()
#     while proof[:2] != "00":
#         ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
#         content = str(ran)
#         rawHash = hashlib.sha256(content.encode())
#         proof = rawHash.hexdigest()
#         print(proof)
#
#     end = time.time()
#     total_time = end - start
#     times.append(total_time)
#
# print(f"Average time: {numpy.average(times)}")
from Block import Block
from Blockchain import Blockchain

blockchain = Blockchain()
block1 = Block(1, ["transaction1", "transaction2"], 100, "prev_hash", "curr_hash_b1")
block2 = Block(2, ["transaction3", "transaction4"], 200, "curr_hash_b1", "curr_hash_b2")
block3 = Block(3, ["transaction5", "transaction6"], 300, "curr_hash_b2", "curr_hash_b3")
blockchain.add_transaction("transaction7")


blockchain.add_new_block(block1)
blockchain.add_new_block(block2)
blockchain.add_new_block(block3)

json_bc = _pickle.dumps(blockchain)


if isinstance(_pickle.loads(json_bc), Blockchain):
    newbc = _pickle.loads(json_bc)
    print(newbc.get_previous_block().index)
    print("IS instance")
