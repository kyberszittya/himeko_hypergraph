import typing

from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge


class QueryOperator(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int,
                 serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphElement]):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)


class QueryInvalidOperands(Exception):
    pass

