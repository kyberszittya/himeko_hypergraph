from himeko.common.clock import NullClock
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation
from himeko.transformations.ros.robot_queries import FactoryRobotQueryElements


class RosControlConfigurationClass():

    def __init__(self, meta_kinematics, clock=None):
        if not meta_kinematics:
            raise ValueError("Meta kinematics is required")
        self._meta_kinematics = meta_kinematics
        # Clock setup
        if clock is not None:
            self._clock = clock
        else:
            self._clock = NullClock()
        # Op query of joints
        self.factory_robot_queries = FactoryRobotQueryElements(self._meta_kinematics, self._clock)
        self._op_query_joint = self.factory_robot_queries.create_query_joint_stereotype()
        # Revolute joint
        self._revolute_joint = self._meta_kinematics["rev_joint"]

    def __create_joint_text_list(self, joints, indent=6):
        res = ""
        for joint in joints:
            joint: HyperEdge
            if self._revolute_joint in joint.stereotype.leaf_stereotypes:
                res += " "*indent + f"- {joint.name}\n"
        return res


    def create_control_configuration(self, robot):
        joints = self._op_query_joint(robot)
        # Select control configuration by stereotype
        control_element = self._meta_kinematics["elements"]["control"]
        op_control = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "control_stereotype", 0,
            control_element
        )
        control_element = op_control(control_element, robot)[0]

        return \
        f"""
controller_manager:
  ros__parameters:
    update_rate: {int(control_element["update_rate"].value)}
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
    force_torque_sensor_controller:
      type: force_torque_sensor_controller/ForceTorqueSensorController
    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController
    forward:velocity_controller:
      type: velocity_controllers/JointVelocityController
    forward:position_controller:
      type: position_controllers/JointPositionController
joint_trajectory_controller:
  ros__parameters:
    joints:
{self.__create_joint_text_list(joints)}
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity
    state_publish_rate: 100.0
    action_monitor_rate: 20.0
    allow_partial_joints_goal: false
speed_scaling_state_broadcaster:
  ros__parameters:
    state_publish_rate: 100.0
forward_velocity_controller:
  ros__parameters:
    joints:
{self.__create_joint_text_list(joints)}
    interface_name: velocity  
       
forward_position_controller:
  ros__parameters:
    joints:
{self.__create_joint_text_list(joints)}       
"""
