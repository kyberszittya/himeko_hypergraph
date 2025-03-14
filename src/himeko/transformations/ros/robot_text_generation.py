import typing

from himeko.common.clock import NullClock
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.ros.generate_launch_python import GenerateLaunch
from himeko.transformations.ros.ros_sim_bridge_config_generation import RosGazeboSimConfigurationGenerator
from himeko.transformations.ros.urdf import TransformationUrdf


class CreateRobotText():

    def __init__(self, meta_kinematics, meta_communications, clock=None):
        self.meta_kinematics = meta_kinematics
        self.meta_communications = meta_communications
        if clock is not None:
            self.clock = clock
        else:
            self.clock = NullClock()
        self.op_transform_urdf: typing.Optional[TransformationUrdf] = None
        self.op_generate_launch: typing.Optional[GenerateLaunch] = None
        self.op_sim_config_generator: typing.Optional[RosGazeboSimConfigurationGenerator] = None


    def create_robot_urdf_text(self):
        self.clock.tick()
        if self.op_transform_urdf is None:
            self.op_transform_urdf = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                TransformationUrdf, "urdf_transformation", self.clock.nano_sec,
                kinematics_meta=self.meta_kinematics, communications_meta=self.meta_communications
            )
        return lambda x: self.op_transform_urdf(x)

    def create_launch_text(self):
        self.clock.tick()
        if self.op_generate_launch is None:
            self.op_generate_launch = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                GenerateLaunch, "generate_launch", self.clock.nano_sec,
                kinematics_meta=self.meta_kinematics, communications_meta=self.meta_communications
            )
        return lambda x: self.op_generate_launch(x)

    def create_sim_configuration_generator(self):
        self.clock.tick()
        if self.op_sim_config_generator is None:
            self.op_sim_config_generator = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                RosGazeboSimConfigurationGenerator, "sim_config_generator", self.clock.nano_sec,
                kinematics_meta=self.meta_kinematics, communications_meta=self.meta_communications
            )
        return lambda x: self.op_sim_config_generator(x)

    @property
    def control_parameters_path(self):
        if self.op_transform_urdf is None:
            return None
        return self.op_transform_urdf.control_param_path

    @staticmethod
    def create_gz_load_launch_file(path, robot):
        name = robot.name
        return f"""gz service -s /world/empty/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 1000 --req 'sdf_filename: "{path}", name: "{name}"'"""
