from himeko.common.clock import AbstractClock, SystemTimeClock
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge
import logging


class HypergraphExecutionEngine(ExecutableHyperEdge):

        def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
            ExecutableHyperEdge.__init__(self, name, timestamp, serial, guid, suid, label, parent)
            self.logger = logging.getLogger(__name__)

        def operate(self, *args, **kwargs):
            self.logger.info(f"Operating on {self.name} with timestamp {self.timestamp}")
            # Check for kwargs for condition field
            if 'condition' in kwargs:
                condition = kwargs['condition']
                # Check if condition is a callable
                if callable(condition):
                    if condition(self):
                        self.logger.info(f"Condition met for {self.name}")
                    else:
                        self.logger.info(f"Condition not met for {self.name}")
                else:
                    self.logger.error(f"Condition is not a callable")
            else:
                self.logger.info(f"No condition provided for {self.name}")
                # Use default condition
                condition = lambda x: True
            for child in self.get_children(condition):
                self.logger.info(f"Operating on child {child.name}")


def create_engine(name: str, clock: AbstractClock = SystemTimeClock()) \
        -> HypergraphExecutionEngine:
    return HypergraphExecutionEngine(name,
                                     clock.tick(), 0, b'0', b'0', "label", None)