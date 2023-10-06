import typing

from himeko_hypergraph.src.elements.edge import HyperEdge
from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.progeny.robotics.metaelements import RobotComponent, RobotConnection


class KinematicLink(RobotComponent):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)


class KinematicJoint(RobotConnection):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
