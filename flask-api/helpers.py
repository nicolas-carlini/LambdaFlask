import uuid
import hashlib


def hash_password(pswd):
    crypt = hashlib.md5()
    crypt.update(bytes(pswd, encoding='utf-8'))
    hashed = (crypt.hexdigest())

    return hashed


def generate_uid():
    id = str(uuid.uuid1())
    return id