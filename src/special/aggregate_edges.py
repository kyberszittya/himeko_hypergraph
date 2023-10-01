import time
import typing

from himeko_hypergraph.src.elements.edge import ExecutableHyperEdge, HypergraphRelation
from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.factories.creation_elements import FactoryHypergraphElements


class CombineEdgeMaxValues(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HyperVertex]) -> None:
        super().__init__(name, timestamp, serial, guid, suid, label, parent)

    def operate(self, t):
        # TODO finish this
        rels = []
        for r in self.in_relations():
            rels.append((r.value, r))
        rels = sorted(rels)
        out_msg = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            t, '_'.join(["combine", self.name]), time.time_ns(),
        )
        for r in rels:
            r: HypergraphRelation
            n: HyperVertex = r.target


        for o in self.out_vertices():
            o: HyperVertex



