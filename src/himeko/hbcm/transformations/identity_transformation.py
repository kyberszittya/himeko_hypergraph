import typing

from himeko.hbcm.elements.edge import EnumHyperarcDirection
from himeko.hbcm.progeny.execution.execution_graph import FlowVertex


class IdentityFlowVertex(FlowVertex):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None, transform_func: typing.Optional[typing.Callable] = None,
                 flow_direction: EnumHyperarcDirection = EnumHyperarcDirection.UNDEFINED):
        super().__init__(name, timestamp, serial, guid, suid, label, parent, transform_func, flow_direction)

    def _input_operation(self, x):
        return x

    def _output_operation(self, x):
        return x

    def _bidirectional_operation(self, x):
        return x
