import hashlib
import math
import time
import string
import random

import numpy

times = list()
for i in range(20):

    start = time.time()
    S = 10  # number of characters in the string.
    # call random.choices() string module to find the string in Uppercase + numeric data.
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
    content = str(ran)
    rawHash = hashlib.sha256(content.encode())
    proof = rawHash.hexdigest()
    while proof[:2] != "00":
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
        content = str(ran)
        rawHash = hashlib.sha256(content.encode())
        proof = rawHash.hexdigest()
        print(proof)

    end = time.time()
    total_time = end - start
    times.append(total_time)

print(f"Average time: {numpy.average(times)}")
