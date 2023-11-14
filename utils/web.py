from urllib.parse import urlparse
from utils.call_counter import CallCounter
import requests

cc = CallCounter(calls_per_second=1)


def is_valid_url(string: str) -> bool:
    return all(urlparse(string)[:1])


def make_request(url: str, respect_rate_limit: bool = True, *args, **kwargs) -> requests.Response:
    """
    Make a GET request trying to respect the rate limit (optional)

    :param url: URL
    :param respect_rate_limit: Whether to honor the rate limit
    :return: `requests.Response`
    """
    if respect_rate_limit:
        cc.hold_until_can_make_request()

    cc.record_call()
    return requests.get(url, *args, **kwargs)
