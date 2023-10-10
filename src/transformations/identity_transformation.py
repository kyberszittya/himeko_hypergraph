import typing

from himeko_hypergraph.src.elements.edge import EnumRelationDirection
from himeko_hypergraph.src.progeny.execution.execution_graph import FlowRequestVertex


class IdentityFlowVertex(FlowRequestVertex):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None, transform_func: typing.Optional[typing.Callable] = None,
                 flow_direction: EnumRelationDirection = EnumRelationDirection.UNDEFINED):
        super().__init__(name, timestamp, serial, guid, suid, label, parent, transform_func, flow_direction)

    def _input_operation(self, x):
        return x

    def _output_operation(self, x):
        return x

    def _bidirectional_operation(self, x):
        return x
