from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge


class TransformationMxw(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)


    def operate(self, *args, **kwargs):
        if self._named_attr["mxw_meta"] is None:
            raise ValueError("MaxWhere kinematics meta not set")
