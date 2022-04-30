import hashlib
import json


def calculate_hash(data):
    """
    Hashes data with sha256 and returns the digest
    :param data: Any type that is json convertible
    :return: digest string
    """
    data_json = json.dumps(data, sort_keys=True)
    data_json_encoded = data_json.encode()
    raw_hash = hashlib.sha256(data_json_encoded)
    digest = raw_hash.hexdigest()
    return digest
