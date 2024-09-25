from himeko.common.clock import AbstractClock, SystemTimeClock
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge


class HypergraphExecutionEngine(ExecutableHyperEdge):

        def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
            ExecutableHyperEdge.__init__(self, name, timestamp, serial, guid, suid, label, parent)

        def operate(self, *args, **kwargs):
            pass


def create_engine(name: str, clock: AbstractClock = SystemTimeClock()) \
        -> HypergraphExecutionEngine:
    return HypergraphExecutionEngine(name,
                                     clock.tick(), 0, b'0', b'0', "label", None)