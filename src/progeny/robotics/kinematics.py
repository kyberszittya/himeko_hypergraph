import typing

from himeko_hypergraph.src.elements.attribute import HypergraphAttribute
from himeko_hypergraph.src.elements.edge import HyperEdge
from himeko_hypergraph.src.elements.element import HypergraphMetaElement
from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.factories.creation_elements import FactoryHypergraphElements
from himeko_hypergraph.src.progeny.robotics.metaelements import RobotComponent, RobotConnection

class Translate(HypergraphAttribute):

    def __init__(self, name: str, value: typing.Any, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphMetaElement] = None, 
                 translation_vector: typing.Optional[typing.Iterable] = None) -> None:
        super().__init__(name, value, timestamp, serial, guid, suid, label, parent)
        self.translation_vector = translation_vector
    

class Quaternion(HypergraphAttribute):

    def __init__(self, name: str, value: typing.Any, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphMetaElement] = None, 
                 rotation_vector: typing.Optional[typing.Iterable] = None) -> None:
        super().__init__(name, value, timestamp, serial, guid, suid, label, parent)
        self.rotation = self.__create_quaternion(rotation_vector)

    def normalize(self):
        raise NotImplementedError

    def __create_quaternion(self, rotation_vector):
        pass


class KinematicState(HyperVertex):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None,
                 translation: typing.Optional[typing.Iterable] = None, rotation: typing.Optional[typing.Iterable] = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self["translation"] = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            Quaternion,f"{name}_rotation", timestamp, self, translation_vector=translation)
        # TODO: convert to quaternion
        self["rotation"] = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            Quaternion,f"{name}_rotation", timestamp, self, rotation_vector=rotation)


class KinematicLink(RobotComponent):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)


class KinematicJoint(RobotConnection):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
