from himeko.common.clock import NullClock
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation


class FactoryRobotQueryElements():

    def __init__(self, meta_kinematics, clock=None):
        if not meta_kinematics:
            raise ValueError("Meta kinematics is required")
        self.kinematics_meta = meta_kinematics
        self.link_element = self.kinematics_meta["elements"]["link"]
        self.joint_element = self.kinematics_meta["elements"]["joint"]
        # Op query
        self.link_op_query = None
        self.joint_op_query = None
        # Clock
        if clock is not None:
            self.clock = clock
        else:
            self.clock = NullClock()


    def create_query_link_stereotype(self, depth=None):
        self.clock.tick()
        if self.link_op_query is None:
            self.link_op_query = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                QueryIsStereotypeOperation, "link_stereotype", self.clock.nano_sec
            )
        return lambda x: self.link_op_query(self.link_element, x, depth=depth)

    def create_query_joint_stereotype(self, depth=None):
        self.clock.tick()
        if self.joint_op_query is None:
            self.joint_op_query = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                QueryIsStereotypeOperation, "joint_stereotype", self.clock.nano_sec
            )
        return lambda x: self.joint_op_query(self.joint_element, x, depth=depth)


