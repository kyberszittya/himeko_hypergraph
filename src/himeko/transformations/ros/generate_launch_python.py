from queue import Queue

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
        # Joint definition
        self._joint_definition = self._kinematics_meta["elements"]["joint"]
        # Sensor element
        self._sensor_element = self._kinematics_meta["elements"]["sensor"]
        # Sensor connection
        self._sensor_connection = self._kinematics_meta["sensors"]["sensor_connection"]
        # Fixed joint
        self._fixed_joint = self._kinematics_meta["fixed_joint"]
        # Nodes to publish
        self.nodes_to_publish = []

    def is_simulation(self, root):
        return len(list(root.get_children(lambda x: self._sim_plugin in x.stereotype))) > 0

    def __get_sensor_link(self, robot: HyperVertex, sensor):
        for connection in robot.get_children(lambda x: self._sensor_connection in x.stereotype and sensor in x.in_vertices()):
            return list(connection.out_vertices())

    def __get_root_link_of_sensor(self, robot: HyperVertex, sensor):
        # Get sensor link
        sensor_link = self.__get_sensor_link(robot, sensor)[0]
        # Put the sensor link in the fringe
        fringe = Queue()
        fringe.put(sensor_link)
        # Select joints
        while not fringe.empty():
            sensor_link = fringe.get()
            sensor_joints = robot.get_children(lambda x: self._joint_definition in x.stereotype and sensor_link in x.out_vertices())
            for joint in sensor_joints:
                joint: HyperEdge
                if self._fixed_joint in joint.stereotype:
                    for v in joint.in_vertices():
                        fringe.put(v)
        if sensor_link is None:
            raise ValueError(f"Sensor {sensor.name} has no link")
        return sensor_link

    def collect_nodes_to_start(self, root):
        res = f"""
    nodes_to_start = [
"""
        for n in self.nodes_to_publish:
            res += 8*' ' + f"""{n},\n"""

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
            # Nodes to publish
            self.nodes_to_publish.append("robot_state_publisher_node")
            self.nodes_to_publish.append("joint_state_broadcaster_spawner")
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
            # Add nodes to publish
            self.nodes_to_publish.append("gz_sim_bridge")
            # Get topic definitions
            for _t in root.get_children(lambda x: self._topic in x.stereotype):
                _t: HyperEdge
                __node_name = f"""gz_sim_bridge_{_t.name}"""
                res += f"""            
    {__node_name} = Node(
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
                # Add nodes to publish
                self.nodes_to_publish.append(__node_name)
                # Add static tf subscribers
                for _sensor in filter(lambda x: self._sensor_element in x.stereotype, _t.out_vertices()):
                    sensor: HyperVertex = _sensor
                    tf = self.__get_root_link_of_sensor(root, sensor)
                    sensor_link = self.__get_sensor_link(root, sensor)[0]
                    tf_link_name = '/'.join([root.name, tf.name, _sensor.name])
                    tf_publisher_node_name = f"""gz_static_tf_publisher_{tf.name}_{sensor.name}"""
                    res += f"""
    {tf_publisher_node_name} = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="{tf_publisher_node_name}",
        arguments=["0", "0", "0", "0", "0", "0", "{sensor_link.name}", "{tf_link_name}"],
        output="screen"
    )
"""
                    # Add nodes to publish
                    self.nodes_to_publish.append(tf_publisher_node_name)
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
            spawner_started_node_name = f"""intitial_{_c.name}_spawner_started"""
            spawner_stopped_node_name = f"""intitial_{_c.name}_spawner_stopped"""
            res += f"""
    # There may be other controllers of the joints, but this is the initially-started one
    {spawner_started_node_name} = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[intitial_{_c.name}, "-c", "/controller_manager"],
        condition=IfCondition(activate_{_c.name}),
    )
    {spawner_stopped_node_name} = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[intitial_{_c.name}, "-c", "/controller_manager", "--stopped"],
        condition=UnlessCondition(activate_{_c.name}),
    )
"""
            # Add nodes to publish
            self.nodes_to_publish.append(spawner_started_node_name)
            self.nodes_to_publish.append(spawner_stopped_node_name)
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

