import abc
import time
import datetime

class AbstractClock(abc.ABC):

    def __init__(self):
        self._time_nsec = 0
        self._time_secs = 0
        # Date

    @abc.abstractmethod
    def _update_time(self) -> int:
        raise NotImplementedError

    def tick(self) -> int:
        self._time_nsec = self._update_time()
        return self.nano_sec

    @property
    def nano_sec(self) -> int:
        return self._time_nsec

    @property
    def secs(self):
        val = self.nano_sec
        return val / 1e9

    @property
    def date(self):
        val = self.nano_sec
        return datetime.datetime.fromtimestamp(val / 1e9)


class SystemTimeClock(AbstractClock):

    def __init__(self):
        super().__init__()

    def _update_time(self) -> int:
        return int(time.time() * 1e9)


class NullClock(AbstractClock):
    """
    Null clock is used for testing purposes

    Avoid using it in production code
    """

    def __init__(self):
        super().__init__()

    def _update_time(self) -> int:
        return 0
