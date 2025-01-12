from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.transformations.meta_generators import MetaKinematicGenerator


class GenerateLaunch(MetaKinematicGenerator):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None, communications_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent, kinematics_meta, communications_meta)
        # Get control definition
        self._control_definition = self._kinematics_meta["elements"]["control_definition"]
        self._sim_plugin = self._kinematics_meta["sim_plugin"]
        self._topic_definition = self._communications_meta["topic_definition"]
        self._topic = self._communications_meta["topic"]
        # Get meta controller
        self.meta_controller = self._kinematics_meta["controllers"]["meta_controller"]

    def is_simulation(self, root):
        return len(list(root.get_children(lambda x: self._sim_plugin in x.stereotype))) > 0

    def collect_nodes_to_start(self, root):
        res = f"""
    nodes_to_start = [
        robot_state_publisher_node,
        joint_state_broadcaster_spawner,
"""
        for _c in root.get_children(lambda x: self.meta_controller in x.stereotype):
            res += f"""
        intitial_{_c.name}_spawner_started,
        intitial_{_c.name}_spawner_stopped,
"""
        is_simulation = self.is_simulation(root)
        if is_simulation:
            res += f"""
        gz_sim_bridge,
"""
            # Get topic definitions
            for _t in root.get_children(lambda x: self._topic in x.stereotype):
                res += f"""
        gz_sim_bridge_{_t.name},
"""
        res += f"""
    ]
"""
        return res



    def generate_joint_state_publisher(self, root):
        res = ""
        is_simulation = self.is_simulation(root)
        for _c in root.get_children(lambda x: self._control_definition in x.stereotype):
            res += f"""
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{{"use_sim_time": {is_simulation}}}, robot_description],
    )
    # Start the joint state broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
"""
        return res

    def generate_simulation_bridge(self, root):
        res = ""
        is_simulation = self.is_simulation(root)
        if is_simulation:
            res += f"""
    gz_sim_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
        output="screen"
    )    
            """
            # Get topic definitions
            for _t in root.get_children(lambda x: self._topic in x.stereotype):
                _t: HyperEdge
                res += f"""            
    gz_sim_bridge_{_t.name} = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="camera_bridge",
        parameters=[{{
            'use_sim_time': True,
            'config_file': "{_t.name}.yaml"
        }}],
        output="screen"
    )
"""
        return res


    def generate_controllers_definitions(self, controllers):
        res = ""
        for _c in controllers:
            res += f"""
    activate_{_c.name} = LaunchConfiguration("activate_{_c.name}")
    intitial_{_c.name} = "{_c.name}"
"""
        return res

    def generate_controller_spawner(self, controllers):
        res = ""
        for _c in controllers:
            res += f"""
    # There may be other controllers of the joints, but this is the initially-started one
    intitial_{_c.name}_spawner_started = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[intitial_{_c.name}, "-c", "/controller_manager"],
        condition=IfCondition(activate_{_c.name}),
    )
    intitial_{_c.name}_spawner_stopped = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[intitial_{_c.name}, "-c", "/controller_manager", "--stopped"],
        condition=UnlessCondition(activate_{_c.name}),
    )
"""
        return res


    def generate_declared_arguments(self, controllers):
        res = ""
        for _c in controllers:
            res += f"""
    declared_arguments.append(
        DeclareLaunchArgument(
            "activate_{_c.name}",
            default_value="true",
            description="Enable headless mode for robot control ({_c.name})",
        )
    )
"""
        return res

    def generate_launch(self, root: HyperVertex):

        # Get controllers
        controllers = [_controller for _controller in root.get_children(lambda x: self.meta_controller in x.stereotype)]


        # Generate launch
        return f"""
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    IfElseSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def launch_setup(context, *args, **kwargs):
{self.generate_controllers_definitions(controllers)}
    urdf_content = open("{root.name}.urdf").read()
    robot_description = {{"robot_description": urdf_content}}
{self.generate_joint_state_publisher(root)}
{self.generate_controller_spawner(controllers)}
{self.generate_simulation_bridge(root)}
{self.collect_nodes_to_start(root)}
    return nodes_to_start

def generate_launch_description():
    declared_arguments = []
{self.generate_declared_arguments(controllers)}
    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
"""

    def operate(self, *args, **kwargs):
        if self._kinematics_meta is None:
            raise ValueError("Kinematics meta is not defined")
        root = args[0]
        # Generate launch
        return self.generate_launch(root)

