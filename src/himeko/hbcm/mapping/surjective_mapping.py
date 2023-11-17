import typing

from himeko.hbcm.elements.edge import HyperEdge, EnumRelationDirection
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements


def surjective_mapping(name: str, timestamp: int, inputs: typing.Iterable[HyperVertex], output: HyperVertex,
                       domain: typing.Optional[HyperVertex] = None):
    e: HyperEdge = FactoryHypergraphElements.create_edge_default(name, timestamp, domain)
    # Inputs
    for i in inputs:
        e.associate_vertex((i, EnumRelationDirection.IN, 1.0))
    # Output
    e.associate_vertex((output, EnumRelationDirection.OUT, 1.0))
    # Return new mapping
    return e


def surjective_connection(name: str, timestamp: int, inputs: typing.Iterable[typing.Any], output: typing.Any,
                          domain: HyperVertex, query: typing.Callable[[HyperVertex, typing.Any], bool]):
    inputs_v = []
    for lb in inputs:
        e = list(domain.get_subelements(lambda x1, x2=lb: query(x1, lb)))[0]
        inputs_v.append(e)
    ou = list(domain.get_subelements(lambda x1: query(x1, output)))[0]
    e = surjective_mapping(name, timestamp, inputs_v, ou, domain)
    return e


def surjective_constructor_mapping(
        t, name: str, timestamp: int, inputs: typing.Iterable[HyperVertex], output: HyperVertex,
        domain: typing.Optional[HyperVertex] = None, input_values: typing.Optional[typing.Iterable] = None, **kwargs):
    e: HyperEdge = FactoryHypergraphElements.create_edge_constructor_default(t, name, timestamp, domain, **kwargs)
    # Inputs
    if input_values is None:
        for i in inputs:
            e.associate_vertex((i, EnumRelationDirection.IN, 1.0))
    else:
        for k, i in enumerate(inputs):
            e.associate_vertex((i, EnumRelationDirection.IN, input_values[k]))
    # Output
    e.associate_vertex((output, EnumRelationDirection.OUT, 1.0))
    # Return new mapping
    return e


def surjective_constructor_connection(
        t, name: str, timestamp: int, inputs: typing.Iterable[typing.Any], output: typing.Any,
        domain: HyperVertex, query: typing.Callable[[HyperVertex, typing.Any], bool]):
    inputs_v = []
    for lb in inputs:
        e = list(domain.get_subelements(lambda x1, x2=lb: query(x1, lb)))[0]
        inputs_v.append(e)
    ou = list(domain.get_subelements(lambda x1: query(x1, output)))[0]
    e = surjective_constructor_mapping(t, name, timestamp, inputs_v, ou, domain)
    return e

