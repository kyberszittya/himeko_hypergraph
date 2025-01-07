from himeko.common.clock import NullClock
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
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
        self.__joint = self._meta_kinematics["elements"]["joint"]
        self._revolute_joint = self._meta_kinematics["rev_joint"]
        # Meta controller type
        self.meta_controller = self._meta_kinematics["controllers"]["meta_controller"]

    def __create_joint_text_list(self, joints, indent=6):
        res = ""
        for joint in joints:
            joint: HyperEdge
            if self._revolute_joint in joint.stereotype.leaf_stereotypes:
                res += " "*indent + f"- {joint.name}\n"
        return res

    def generate_text_controller_manager(self, robot):
        controller_manager_controllers = ""
        indent = 4
        for c in robot.get_children(lambda x: self.meta_controller in x.stereotype):
            controller_manager_controllers += indent*" " + c.name + ":\n"
            controller_manager_controllers += (indent + 2)*" " + "type: " + c["type"].value + "\n"
        return controller_manager_controllers


    def create_control_configuration(self, robot):
        robot: HyperVertex
        joints = self._op_query_joint(robot)
        # Select control configuration by stereotype
        control_element = self._meta_kinematics["elements"]["control"]

        op_control = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "control_stereotype", 0,
            control_element
        )
        control_element = op_control(control_element, robot)[0]
        controller_manager_controllers = self.generate_text_controller_manager(robot)

        controllers_def_text = ""
        indent = 0
        # Create controller configuration
        for c in robot.get_children(lambda x: self.meta_controller in x.stereotype):
            controllers_def_text += indent*" " + c.name + ":\n"
            sub_indent = indent
            sub_indent += 2
            controllers_def_text += (sub_indent * " ") + "ros__parameters:\n"
            # Get joint list
            joints = filter(lambda x: self.__joint in x.target.stereotype, c["joints"].out_relations())
            joints = map(lambda x: x.target, joints)
            controllers_def_text += (sub_indent * " ") + "joints:\n"
            controllers_def_text += self.__create_joint_text_list(joints, sub_indent + 2)
            controllers_def_text += (sub_indent * " ") + "command_interfaces:\n"
            # Command interfaces (incoming relations of interfaces edge)
            command_interfaces = c["interfaces"].in_relations()
            for ci in command_interfaces:
                controllers_def_text += (sub_indent + 2) * " " + "- " + ci.target.name + "\n"
            controllers_def_text += (sub_indent * " ") + "state_interfaces:\n"
            # State interfaces (outgoing relations of interfaces edge)
            state_interfaces = c["interfaces"].out_relations()
            for si in state_interfaces:
                controllers_def_text += (sub_indent + 2) * " " + "- " + si.target.name + "\n"

            # Publish rate
            controllers_def_text += (sub_indent * " ") + f"state_publish_rate: {c['state_publish_rate'].value}\n"
            controllers_def_text += (sub_indent * " ") + f"action_monitor_rate: {c['action_monitor_rate'].value}\n"
            # Partial joints goal
            controllers_def_text += (sub_indent * " ") + "allow_partial_joints_goal: false\n"

        return \
        f"""
controller_manager:
  ros__parameters:
    update_rate: {int(control_element["update_rate"].value)}
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
{controller_manager_controllers}
{controllers_def_text}       
"""
