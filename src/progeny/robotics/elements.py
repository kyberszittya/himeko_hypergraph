import typing

from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.progeny.robotics.kinematics import KinematicJoint, KinematicLink
from himeko_hypergraph.src.progeny.robotics.metaelements import RobotComponent, RobotConnection


class RobotNode(HyperVertex):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)

    @property
    def links(self):
        return self.get_children(lambda x: isinstance(x, KinematicLink))

    @property
    def joints(self):
        return self.get_children(lambda x: isinstance(x, KinematicJoint))

    @property
    def robot_elements(self):
        return self.get_children(lambda x: isinstance(x, RobotComponent) or isinstance(x, RobotConnection))
