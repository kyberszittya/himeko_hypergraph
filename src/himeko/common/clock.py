import abc
import time


class AbstractClock(abc.ABC):

    def __init__(self):
        self._time_nsec = 0
        self._time_secs = 0
        # Date

    @abc.abstractmethod
    def tick(self) -> int:
        raise NotImplementedError

    @property
    def nano_sec(self) -> int:
        self.tick()
        return self._time_nsec

    @property
    def secs(self):
        self.tick()
        return self._time_secs

    @property
    def date(self):
        # TODO: finish date handling
        self.tick()


class SystemTimeClock(AbstractClock):

    def __init__(self):
        super().__init__()

    def tick(self) -> int:
        return time.time_ns()