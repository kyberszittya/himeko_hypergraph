from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation


class TransformationMxw(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, mxw_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self._named_attr["mxw_meta"] = mxw_meta


    def operate(self, *args, **kwargs):
        if self._named_attr["mxw_meta"] is None:
            raise ValueError("MaxWhere kinematics meta not set")
        root = args[0]
        mxw_node = self["mxw_meta"]["elements"]["mxw_node"]
        op_joint = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "mxw_node_stereotype", 0,
            stereotype=mxw_node
        )
        res_node = op_joint(root, depth=1)
        for r in res_node:
            print(r)
            print(r.name)
