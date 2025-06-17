import typing

from himeko.hbcm.elements.attribute import HypergraphAttribute, HypergraphQueryAttribute
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge
from himeko.hbcm.elements.executable.vertex import ExecutableHyperVertex
from himeko.hbcm.elements.vertex import HyperVertex

import hashlib

from himeko.hbcm.exceptions.basic_exceptions import InvalidIdentification


def create_default_vertex_label(name: str, timestamp: int, serial: int,
                                parent: typing.Optional[HypergraphElement] = None) -> str:
    __attr = [str(x) for x in [name, timestamp, serial]]
    if parent is None:
        return f"{'.'.join(__attr)}"
    return f"{parent.label}//{'.'.join(__attr)}"


def create_default_global_vertex_label(name: str, timestamp: int,
                                       parent: typing.Optional[HypergraphElement] = None) -> str:
    __attr = [str(x) for x in [name, timestamp]]
    if parent is None:
        return f"{'.'.join(__attr)}"
    return f"{parent.label}//{'.'.join(__attr)}"


def create_default_global_edge_label(name: str, timestamp: int,
                                     parent: typing.Optional[HypergraphElement] = None) -> str:
    __attr = [str(x) for x in [name, timestamp]]
    if parent is None:
        return f"{'.'.join(__attr)}"

    return f"{parent.label}//{'.'.join(__attr)}"


def create_default_edge_label(name: str, timestamp: int, serial: int,
                                parent: typing.Optional[HypergraphElement] = None) -> str:
    __attr = [str(x) for x in [name, timestamp, serial]]
    if parent is None:
        return f"{'.'.join(__attr)}"
    return f"{parent.label}||{'.'.join(__attr)}"


def create_default_vertex_guid(name: str, timestamp: int,
                               parent: typing.Optional[HypergraphElement] = None) -> bytes:
    return hashlib.sha384(create_default_global_vertex_label(name, timestamp, parent).encode('utf-8')).digest()


def create_default_vertex_suid(name: str, timestamp: int, serial: int,
                               parent: typing.Optional[HypergraphElement] = None) -> bytes:
    return hashlib.sha384(create_default_vertex_label(name, timestamp, serial, parent).encode('utf-8')).digest()


def create_default_edge_guid(name: str, timestamp: int, serial: int,
                               parent: typing.Optional[HypergraphElement] = None) -> bytes:
    return hashlib.sha384(create_default_edge_label(name, timestamp, serial, parent).encode('utf-8')).digest()


def create_default_edge_suid(name: str, timestamp: int,
                             parent: typing.Optional[HypergraphElement] = None) -> bytes:
    return hashlib.sha384(create_default_global_edge_label(name, timestamp, parent).encode('utf-8')).digest()


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


def global_serial(name: str, timestamp: int, parent: typing.Optional[HypergraphElement] = None):
    if parent is None:
        serial = 0
    else:
        serial = create_parent_based_serial(parent)
    __attr = [str(x) for x in [name, timestamp, serial]]
    return int.from_bytes(hashlib.sha384('.'.join(__attr).encode('utf-8')).digest(), 'big')


def create_default_vertex_id_values(name: str, timestamp: int, parent: typing.Optional[HypergraphElement] = None):
    if parent is None:
        serial = 0
    else:
        serial = create_parent_based_serial(parent)
    # Global serial
    label = create_default_global_vertex_label(name, timestamp, parent)
    guid = create_default_vertex_guid(name, timestamp, parent)
    suid = create_default_vertex_suid(name, timestamp, serial, parent)
    return label, serial, guid, suid


def create_default_edge_id_values(name: str, timestamp: int, parent):
    serial = create_parent_based_serial(parent)
    label = create_default_global_edge_label(name, timestamp, parent)
    guid = create_default_edge_guid(name, timestamp, parent)
    suid = create_default_vertex_suid(name, timestamp, serial, parent)
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
    def create_edge_default(cls, name: str, timestamp: int, parent: HyperVertex) -> HyperEdge:
        serial = len(parent)
        label = create_default_edge_label(name, timestamp, serial, parent)
        guid = create_default_edge_guid(name, timestamp, serial, parent)
        suid = create_default_suid(guid, parent.suid)
        e0 = HyperEdge(name, timestamp, serial, guid, suid, label, parent)
        return e0

    @classmethod
    def create_vertex_constructor_default(cls, t, name: str, timestamp: int,
                                          parent: typing.Optional[HyperVertex] = None) \
            -> HyperVertex|ExecutableHyperVertex:
        label, serial, guid, suid = cls.create_default_attributes(name, timestamp, parent)
        v0 = t(name, timestamp, serial, guid, suid, label, parent)
        return v0

    @classmethod
    def create_vertex_constructor_default_kwargs(cls, t, name: str, timestamp: int,
                                                 parent: typing.Optional[HyperVertex] = None,
                                                 **kwargs):
        label, serial, guid, suid = cls.create_default_attributes(name, timestamp, parent)
        v0 = t(name, timestamp, serial, guid, suid, label, parent, **kwargs)
        return v0

    @classmethod
    def create_attribute_default(cls, name: str, value: typing.Any, type: str, timestamp: int, parent: HyperVertex):
        label, serial, guid, suid = cls.create_default_attributes(name, timestamp, parent)
        a0 = HypergraphAttribute(name, value, type, timestamp, serial, guid, suid, label, parent)
        return a0

    @classmethod
    def create_query_attribute_default(cls, name: str, value: typing.Any, type: str, timestamp: int, parent: HyperVertex):
        label, serial, guid, suid = cls.create_default_attributes(name, timestamp, parent)
        a0 = HypergraphQueryAttribute(name, value, type, timestamp, serial, guid, suid, label, parent)
        return a0

    @classmethod
    def create_edge_constructor_default(cls, t, name: str, timestamp: int, parent: HyperVertex, **kwargs) \
            -> HyperEdge|ExecutableHyperEdge:
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

# Create a factory class to use an associated clock

class FactoryHypergraphElementsClock(FactoryHypergraphElements):

    def __init__(self, clock):
        self.clock = clock

    def create_vertex(self, name: str, parent: typing.Optional[HyperVertex] = None):
        timestamp = self.clock.nano_sec
        return super().create_vertex_default(name, timestamp, parent)

    def create_edge(self, name: str, parent: HyperVertex):
        timestamp = self.clock.nano_sec
        return super().create_edge_default(name, timestamp, parent)

    def create_vertex_constructor(self, t, name: str, parent: typing.Optional[HyperVertex] = None):
        timestamp = self.clock.nano_sec
        return super().create_vertex_constructor_default(t, name, timestamp, parent)

    def create_vertex_constructor_kwargs(self, t, name: str, parent: typing.Optional[HyperVertex] = None, **kwargs):
        timestamp = self.clock.nano_sec
        return super().create_vertex_constructor_default_kwargs(t, name, timestamp, parent, **kwargs)

    def create_attribute(self, name: str, value: typing.Any, type: str, parent: HyperVertex):
        timestamp = self.clock.nano_sec
        return super().create_attribute_default(name, value, type, timestamp, parent)

    def create_edge_constructor(self, t, name: str, parent: HyperVertex, **kwargs):
        timestamp = self.clock.nano_sec
        return super().create_edge_constructor_default(t, name, timestamp, parent, **kwargs)

