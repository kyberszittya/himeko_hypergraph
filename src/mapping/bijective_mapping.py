import typing

from himeko_hypergraph.src.elements.edge import EnumRelationDirection
from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.factories.creation_elements import FactoryHypergraphElements


def bijective_mapping(t, name:str, timestamp: int,  i: HyperVertex, o: HyperVertex, parent: typing.Optional[HyperVertex] = None):
    __e = FactoryHypergraphElements.create_edge_constructor_default(t, name, timestamp, parent)
    __e.associate_vertex((i, EnumRelationDirection.IN, 1.0))
    __e.associate_vertex((o, EnumRelationDirection.OUT, 1.0))
    return __e
