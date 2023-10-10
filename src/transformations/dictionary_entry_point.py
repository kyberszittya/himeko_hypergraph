import typing

from himeko_hypergraph.src.elements.edge import EnumRelationDirection
from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.progeny.execution.execution_graph import FlowRequestVertex


class DictFlowVertex(FlowRequestVertex):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None, transform_func: typing.Optional[typing.Callable] = None,
                 flow_direction: EnumRelationDirection = EnumRelationDirection.UNDEFINED):
        super().__init__(name, timestamp, serial, guid, suid, label, parent, transform_func, flow_direction)

    def _input_operation(self, *args, **kwargs):
        pass

    def _output_operation(self, vertex: HyperVertex):
        resp = dict()
        for v in vertex.get_subelements(lambda x: isinstance(x, HyperVertex)):
            v: HyperVertex
            if len(v.attribute_names) > 0:
                _node_dict = dict()
                for _a in v.attribute_names:
                    _node_dict[_a] = v[_a]
                resp[v.name] = _node_dict
        return resp

    def _bidirectional_operation(self, *args, **kwargs):
        pass
