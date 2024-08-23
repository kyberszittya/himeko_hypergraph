import typing

from himeko.hbcm.elements.edge import EnumRelationDirection
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements


def bijective_mapping(t, name:str, timestamp: int,  i: HyperVertex, o: HyperVertex,
                      parent: typing.Optional[HyperVertex] = None, **kwargs):
    __e = FactoryHypergraphElements.create_edge_constructor_default(t, name, timestamp, parent, **kwargs)
    __e.associate_vertex((i, EnumRelationDirection.IN, 1.0))
    __e.associate_vertex((o, EnumRelationDirection.OUT, 1.0))
    return __e
