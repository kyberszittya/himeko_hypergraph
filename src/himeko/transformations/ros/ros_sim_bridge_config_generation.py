from himeko.common.clock import NullClock
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex


class RosGazeboSimConfigurationGenerator():

    def __init__(self, meta_kinematics, clock=None):
        if not meta_kinematics:
            raise ValueError("Meta kinematics is required")
        self._kinematics_meta = meta_kinematics
        # Clock setup
        if clock is not None:
            self._clock = clock
        else:
            self._clock = NullClock()

    def __ros2_msg(self, topic_type):
        types = topic_type.split('/')
        return '/'.join(types[:-1] + ['msg',  types[-1]])

    def __map_ros2_gazebo(self, topic_type):
        types = topic_type.split('/')
        return '.'.join(['gz', 'msgs', types[-1]])

    def __yaml_entry_generator(self, orig_topic_name, topic_name, topic_type):
        return f"""
- gz_topic_name: "{orig_topic_name}"
  ros_topic_name: "{topic_name}"
  ros_type_name: "{self.__ros2_msg(topic_type)}"
  gz_type_name: "{self.__map_ros2_gazebo(topic_type)}"
  lazy: true
  direction: GZ_TO_ROS
                """


    def generate_gazebo_sim_configuration(self, root):
        sensor_element = self._kinematics_meta["elements"]["sensor"]
        topic_definition = self._kinematics_meta["topic_definition"]
        defs = dict()
        for topic in root.get_children(lambda x: self._kinematics_meta["topic"] in x.stereotype):
            definition_sim_config = ""
            topic: HyperEdge
            # Get topic definitions
            for c in filter(lambda x: topic_definition in x.target.stereotype, topic.in_relations()):
                _topic_def: HyperVertex = c.target
                topic_type = _topic_def["message_type"]
                for sensor in filter(lambda x: sensor_element in x.target.stereotype, topic.out_relations()):
                    sensor: HyperEdge = sensor.target
                    raw_topic_name = _topic_def["topic_name"].value
                    topic_name = '/'.join([root.name, sensor.name, _topic_def["topic_name"].value])
                    definition_sim_config += self.__yaml_entry_generator('/'.join([root.name, raw_topic_name]), topic_name, topic_type.value)
            defs[topic.name] = definition_sim_config
        #
        return defs