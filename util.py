import hashlib


def md5(s: str) -> str: #Calculates and returns the MD5 Hash
    return hashlib.md5(s.encode()).hexdigest()
