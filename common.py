import hashlib


CHUNK = 4096


def md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
