from himeko.common.clock import NullClock
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.ros.urdf import TransformationUrdf


class CreateRobotText():

    def __init__(self, meta_kinematics, clock=None):
        self.meta_kinematics = meta_kinematics
        if clock is not None:
            self.clock = clock
        else:
            self.clock = NullClock()

    def create_robot_urdf_text(self):
        self.clock.tick()
        op_transform_urdf = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            TransformationUrdf, "urdf_transformation", self.clock.nano_sec,
            kinematics_meta=self.meta_kinematics
        )
        return lambda x: op_transform_urdf(x)

    @staticmethod
    def create_gz_load_launch_file(path, robot):
        name = robot.name
        return f"""gz service -s /world/empty/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 1000 --req 'sdf_filename: "{path}", name: "{name}"'"""
