from himeko.hbcm.elements.edge import HyperEdge, HyperArc
from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.transformations.meta_generators import MetaKinematicGenerator


class RosGazeboSimConfigurationGenerator(MetaKinematicGenerator):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None, communications_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent, kinematics_meta, communications_meta)

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
        topic_definition = self._communications_meta["topic_definition"]
        topic = self._communications_meta["topic"]
        defs = dict()
        for topic in root.get_children(lambda x: topic in x.stereotype):
            definition_sim_config = ""
            topic: HyperEdge
            # Get topic definitions
            for c in filter(lambda x: topic_definition in x.target.stereotype, topic.in_relations()):
                _topic_def: HyperVertex = c.target
                topic_type = _topic_def["message_type"]
                for sensor in filter(lambda x: sensor_element in x.target.stereotype, topic.out_relations()):
                    sensor: HyperArc = sensor.target
                    raw_topic_name = _topic_def["topic_name"].value
                    topic_name = '/'.join([root.name, sensor.name, _topic_def["topic_name"].value])
                    definition_sim_config += self.__yaml_entry_generator('/'.join([root.name, raw_topic_name]), topic_name, topic_type.value)
            defs[topic.name] = definition_sim_config
        #
        return defs

    def operate(self, *args, **kwargs):
        if self._kinematics_meta is None:
            raise ValueError("Kinematics meta is not defined")
        if self._communications_meta is None:
            raise ValueError("Communications meta is not defined")
        root = args[0]
        # Generate launch
        return self.generate_gazebo_sim_configuration(root)