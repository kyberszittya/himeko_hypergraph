import typing

from himeko_hypergraph.src.elements.edge import HyperEdge
from himeko_hypergraph.src.elements.element import HypergraphElement
from himeko_hypergraph.src.elements.vertex import HyperVertex

import hashlib

from himeko_hypergraph.src.exceptions.basic_exceptions import InvalidIdentification


def create_default_vertex_label(name: str, timestamp: int, serial: int,
                                parent: typing.Optional[HypergraphElement] = None) -> str:
    __attr = [str(x) for x in [name, timestamp, serial]]
    if parent is None:
        return f"{'.'.join(__attr)}"
    return f"{parent.label}//{'.'.join(__attr)}"


def create_default_edge_label(name: str, timestamp: int, serial: int,
                                parent: typing.Optional[HypergraphElement] = None) -> str:
    __attr = [str(x) for x in [name, timestamp, serial]]
    if parent is None:
        return f"{'.'.join(__attr)}"
    return f"{parent.label}||{'.'.join(__attr)}"


def create_default_vertex_guid(name: str, timestamp: int, serial: int,
                               parent: typing.Optional[HypergraphElement] = None) -> bytes:
    return hashlib.sha384(create_default_vertex_label(name, timestamp, serial, parent).encode('utf-8')).digest()


def create_default_edge_guid(name: str, timestamp: int, serial: int,
                               parent: typing.Optional[HypergraphElement] = None) -> bytes:
    return hashlib.sha384(create_default_edge_label(name, timestamp, serial, parent).encode('utf-8')).digest()


def create_default_suid(uid: bytes, uid1: bytes):
    if len(uid) != len(uid1):
        raise InvalidIdentification("Invalid length of identification")
    n = len(uid)
    suid = int.from_bytes(uid, 'big') & int.from_bytes(uid1, 'big')
    suid = int.to_bytes(suid, n, 'big')
    return suid


def create_parent_based_serial(parent) -> int:
    if parent is None:
        serial = 0
    else:
        serial = len(parent)
    return serial


def create_default_vertex_id_values(name: str, timestamp: int, parent: typing.Optional[HypergraphElement] = None):
    if parent is None:
        serial = 0
    else:
        serial = create_parent_based_serial(parent)
    label = create_default_vertex_label(name, timestamp, serial, parent)
    guid = create_default_vertex_guid(name, timestamp, serial, parent)
    suid = guid
    return label, serial, guid, suid


def create_default_edge_id_values(name: str, timestamp: int, parent):
    serial = create_parent_based_serial(parent)
    label = create_default_edge_label(name, timestamp, serial, parent)
    guid = create_default_edge_guid(name, timestamp, serial, parent)
    suid = guid
    return label, serial, guid, suid


class FactoryHypergraphElements(object):

    @classmethod
    def create_default_attributes(cls, name: str, timestamp: int, parent: typing.Optional[HyperVertex] = None):
        label, serial, guid, suid = create_default_vertex_id_values(name, timestamp, parent)
        if parent is not None:
            n = len(suid)
            suid = int.from_bytes(suid, 'big') & int.from_bytes(parent.guid, 'big')
            suid = int.to_bytes(suid, n, 'big')
        return label, serial, guid, suid

    @classmethod
    def create_vertex_default(cls, name: str, timestamp: int, parent: typing.Optional[HyperVertex] = None):
        label, serial, guid, suid = cls.create_default_attributes(name, timestamp, parent)
        v0 = HyperVertex(name, timestamp, serial, guid, suid, label, parent)
        return v0

    @classmethod
    def create_edge_default(cls, name: str, timestamp: int, parent: HyperVertex):
        serial = len(parent)
        label = create_default_edge_label(name, timestamp, serial, parent)
        guid = create_default_edge_guid(name, timestamp, serial, parent)
        suid = create_default_suid(guid, parent.suid)
        e0 = HyperEdge(name, timestamp, serial, guid, suid, label, parent)
        return e0

    @classmethod
    def create_vertex_constructor_default(cls, t, name: str, timestamp: int, parent: typing.Optional[HyperVertex] = None):
        label, serial, guid, suid = cls.create_default_attributes(name, timestamp, parent)
        v0 = t(name, timestamp, serial, guid, suid, label, parent)
        return v0

    @classmethod
    def create_vertex_constructor_default_kwargs(cls, t, name: str, timestamp: int, parent: typing.Optional[HyperVertex] = None, **kwargs):
        label, serial, guid, suid = cls.create_default_attributes(name, timestamp, parent)
        v0 = t(name, timestamp, serial, guid, suid, label, parent, **kwargs)
        return v0

    @classmethod
    def create_edge_constructor_default(cls, t, name: str, timestamp: int, parent: HyperVertex, **kwargs):
        serial = len(parent)
        label = create_default_edge_label(name, timestamp, serial, parent)
        guid = create_default_edge_guid(name, timestamp, serial, parent)
        suid = create_default_suid(guid, parent.suid)
        e0 = t(name, timestamp, serial, guid, suid, label, parent, **kwargs)
        return e0




def create_vertex_by_labels(names: typing.Iterable[str], timestamp: int, parent: typing.Optional[HyperVertex] = None):
    vertices = []
    for c in names:
        v = FactoryHypergraphElements.create_vertex_default(c, timestamp, parent)
        vertices.append(v)
    return vertices
