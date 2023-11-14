from datetime import datetime
from time import sleep, time
from typing import Optional

from utils.singleton import Singleton


class CallCounter(Singleton):
    """
    A simple call counter

    Tries to make sure that we respect the website's rate limit
    """

    calls_per_second: float
    last_call: float

    _earliest_allowed_time: float

    def __init__(
        self, calls_per_second: float = 1, last_call: Optional[datetime | float] = None
    ):
        self.calls_per_second = calls_per_second
        if not last_call:
            self.last_call = time()
        else:
            self.last_call = (
                last_call.timestamp() if isinstance(last_call, datetime) else last_call
            )
        self._earliest_allowed_time = time()

    def record_call(self):
        self.last_call = time()
        self._earliest_allowed_time = self.last_call + 1 / self.calls_per_second

    def hold_until_can_make_request(self):
        while time() < self._earliest_allowed_time:
            sleep(1)
