from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge


class MetaKinematicGenerator(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None, communications_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        # Kinematics meta data check
        if kinematics_meta is None:
            raise ValueError("Kinematics meta is required")
        self._kinematics_meta = kinematics_meta
        # Communications
        if communications_meta is None:
            raise ValueError("Communications meta is required")
        self._communications_meta = communications_meta
        # Setup kinematics element
        self.__setup_kinematics_element()

    def __setup_kinematics_element(self):

        # Set up stereotypes
        self.geom_box = self._kinematics_meta["geometry"]["box"]
        self.geom_cylinder = self._kinematics_meta["geometry"]["cylinder"]
        self.geom_sphere = self._kinematics_meta["geometry"]["sphere"]
        # Axis
        self.axis_element = self._kinematics_meta["axes"]["axis_definition"]
        # Link and frame
        self.link_element = self._kinematics_meta["elements"]["link"]
        self.frame_element = self._kinematics_meta["elements"]["frame"]
        # Joints
        self.joint_element = self._kinematics_meta["elements"]["joint"]
        self.rev_joint = self._kinematics_meta["rev_joint"]
        self.fixed_joint = self._kinematics_meta["fixed_joint"]
        self.conti_joint = self._kinematics_meta["conti_joint"]
        # Angle
        self.angle_unit = self._kinematics_meta["units"]["angle"].value
        # Operate joint stereotype
        self.op_joint = None
