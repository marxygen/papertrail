from urllib.parse import urlparse


def is_valid_url(string: str) -> bool:
    return all(urlparse(string)[:1])
