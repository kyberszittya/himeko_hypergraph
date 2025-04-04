from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.element import HypergraphElement

from lxml import etree
import numpy as np

from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation
from himeko.transformations.meta_generators import MetaKinematicGenerator


class UrdfGeometricCalculations(object):

    def convert_angles(self, angles, angle_unit):
        match angle_unit:
            case "radian":
                return angles
            case "degree":
                return np.deg2rad(angles)
            case _:
                raise ValueError("Unknown angle")


class TransformationUrdfCameraElements(object):

    def __init__(self, angle_unit):
        self.__angle_unit = angle_unit
        self.__geometric_calculations = UrdfGeometricCalculations()

    def setup_camera_elements(self, sensor):
        # Camera
        camera_xml = etree.Element("camera")
        # FOV
        fov_element = etree.Element("horizontal_fov")
        # Convert angles
        fov_element.text = str(self.__geometric_calculations.convert_angles(sensor["fov"].value[0], self.__angle_unit))
        camera_xml.append(fov_element)
        # Clip values
        clip_element = etree.Element("clip")
        # Image
        image_element = etree.Element("image")
        image_width = etree.Element("width")
        image_width.text = str(int(sensor["image_size"].value[0]))
        image_height = etree.Element("height")
        image_height.text = str(int(sensor["image_size"].value[1]))
        image_element.append(image_width)
        image_element.append(image_height)
        camera_xml.append(image_element)
        # Text values
        near_element = etree.Element("near")
        near_element.text = str(sensor["clip"].value[0])
        far_element = etree.Element("far")
        far_element.text = str(sensor["clip"].value[1])
        clip_element.append(near_element)
        clip_element.append(far_element)
        camera_xml.append(clip_element)
        # Camera XML
        return camera_xml



class TransformationUrdf(MetaKinematicGenerator):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None, communications_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent, kinematics_meta, communications_meta)
        # Control parameters path
        self._control_param_path = None
        # Geometric calculations
        self._geometric_calculations = UrdfGeometricCalculations()
        # Camera elements generator
        self._camera_elements = TransformationUrdfCameraElements(self.angle_unit)
        # Setup root XML
        self.robot_root_xml = etree.Element("robot")




    @property
    def control_param_path(self):
        return self._control_param_path

    @property
    def meta_kinematics(self):
        return self._kinematics_meta

    @meta_kinematics.setter
    def meta_kinematics(self, value):
        if value is None:
            raise ValueError("Kinematics meta is required")
        self._kinematics_meta = value
        self.__setup_kinematics_element()


    @staticmethod
    def __generate_geometry(geometry, *args):
        _box, _cylinder, _sphere = args
        # Create geometry element
        geometry_xml = etree.Element("geometry")
        # Check for different geometries
        if _cylinder in geometry.value.stereotype:
            # Add cylinder
            cylinder_xml = etree.Element("cylinder")
            radius, length = geometry.value["dimension"].value
            cylinder_xml.set("length", str(length))
            cylinder_xml.set("radius", str(radius))
            # Add to geometry
            geometry_xml.append(cylinder_xml)
        elif _box in geometry.value.stereotype:
            # Add box
            box_xml = etree.Element("box")
            size = geometry.value["dimension"].value
            box_xml.set("size", " ".join([str(s) for s in size]))
            # Add to geometry
            geometry_xml.append(box_xml)
        elif _sphere in geometry.value.stereotype:
            # Add sphere
            sphere_xml = etree.Element("sphere")
            radius = geometry.value["dimension"].value[-1]
            sphere_xml.set("radius", str(radius))
            # Add to geometry
            geometry_xml.append(sphere_xml)
        return geometry_xml

    def calc_inertia(self, geometry, mass, *standard_geometries):
        # Get standard geometries
        _box, _cylinder, _sphere = standard_geometries
        ixx, iyy, izz = 1, 1, 1
        ixz, ixy, iyz = 0, 0, 0
        dimensions = geometry["dimension"].value
        if _cylinder in geometry.stereotype:
            # Cylinder
            length, radius = dimensions
            # Calculate inertia
            ixx = (1 / 12) * mass * (3 * radius ** 2 + length ** 2)
            iyy = ixx
            izz = (1 / 2) * mass * radius ** 2
        elif _box in geometry.stereotype:
            # Box
            x, y, z = dimensions
            # Calculate inertia
            ixx = (1 / 12) * mass * (y ** 2 + z ** 2)
            iyy = (1 / 12) * mass * (x ** 2 + z ** 2)
            izz = (1 / 12) * mass * (x ** 2 + y ** 2)
        elif _sphere in geometry.stereotype:
            # Sphere
            r = dimensions[0]
            # Calculate inertia
            ixx = (2 / 5) * mass * r ** 2
            iyy = ixx
            izz = ixx
        return ixx, iyy, izz, ixz, ixy, iyz

    def __add_links(self, root):
        # Geometry
        geometries = [
            self.geom_box,
            self.geom_cylinder,
            self.geom_sphere
        ]
        # Get frames
        op = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "frame_stereotype", 0,
            self.frame_element
        )
        res = op(self.frame_element, root, depth=None)
        # Add frames (single links)
        for link in res:
            link_xml = etree.Element("link")
            link_xml.set("name", link.name)
            # Add link to robot
            self.robot_root_xml.append(link_xml)
        # Get link element
        op = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "link_stereotype", 0,
            self.link_element
        )
        res = op(self.link_element, root, depth=None)
        # Add links
        for link in res:
            link_xml = etree.Element("link")
            link_xml.set("name", link.name)
            # Add link to robot
            self.robot_root_xml.append(link_xml)
            # Inertia
            # Create inertia element
            inertial_xml = etree.Element("inertial")
            # Add inertia to link
            link_xml.append(inertial_xml)
            # Add mass to inertia
            mass_xml = etree.Element("mass")
            mass_xml.set("value", str(link["mass"].value))
            inertial_xml.append(mass_xml)
            # Check if origin is present
            root_origin = None
            if "origin" in link:
                root_origin = link["origin"]
            # Add inertia calculation
            if "inertia" not in link:
                ixx, iyy, izz, ixz, ixy, iyz = self.calc_inertia(
                    link["collision"].value,
                    link["mass"].value,
                    *geometries
                )
            else:
                ixx, iyy, izz, ixz, ixy, iyz = link["inertia"].value
            inertia_xml = etree.Element("inertia")
            inertia_xml.set("ixx", str(ixx))
            inertia_xml.set("iyy", str(iyy))
            inertia_xml.set("izz", str(izz))
            inertia_xml.set("ixz", str(ixz))
            inertia_xml.set("ixy", str(ixy))
            inertia_xml.set("iyz", str(iyz))
            inertial_xml.append(inertia_xml)
            if root_origin is not None:
                # Create root element
                el_root_origin = self.__create_origin(root_origin)
                inertial_xml.append(el_root_origin)
            # Geometry
            _visual = link["visual"]
            # Create visual element
            visual_xml = etree.Element("visual")
            # Add visual to link
            link_xml.append(visual_xml)
            # Add geometry to visual
            visual_geom = self.__generate_geometry(_visual, *geometries)
            # Wrap up
            visual_xml.append(visual_geom)
            if root_origin is not None:
                # Create root element
                el_root_origin = self.__create_origin(root_origin)
                visual_xml.append(el_root_origin)
            # Color
            _color_element = link["color"]
            if isinstance(_color_element.value, HyperVertex) or isinstance(_color_element.value, HypergraphAttribute):
                _color_element = _color_element.value
            _color_xml = etree.Element("material")
            _color_xml.set("name", _color_element.name)
            _color_val_xml = etree.Element("color")
            if len(_color_element.value) == 3:
                _color_val_xml.set("rgb", " ".join([str(x) for x in _color_element.value]))
            elif len(_color_element.value) == 4:
                _color_val_xml.set("rgba", " ".join([str(x) for x in _color_element.value]))
            _color_xml.append(_color_val_xml)
            visual_xml.append(_color_xml)
            # Get collision
            _collision = link["collision"]
            # Create collision element
            collision_xml = etree.Element("collision")
            # Add collision to link
            link_xml.append(collision_xml)
            # Add geometry to collision
            collision_geom = self.__generate_geometry(_collision, *geometries)
            collision_xml.append(collision_geom)
            if root_origin is not None:
                # Create root element
                el_root_origin = self.__create_origin(root_origin)
                collision_xml.append(el_root_origin)

    @staticmethod
    def __add_axis(j, axis_element):
        axis_val = [0] * 3
        axis_xml = etree.Element("axis")
        for ax in filter(lambda x: axis_element in x.target.stereotype, j.out_relations()):
            # Add value to axis
            axis_val[0] = ax.target["ax"].value[0]
            axis_val[1] = ax.target["ax"].value[1]
            axis_val[2] = ax.target["ax"].value[2]
        axis_xml.set("xyz", " ".join([str(a) for a in axis_val]))
        return axis_xml

    def __convert_angles(self, angles):
        return self._geometric_calculations.convert_angles(angles, self.angle_unit)


    def __create_origin(self, value):
        # Add origin
        origin_xml = etree.Element("origin")
        if isinstance(value, HypergraphAttribute):
            origin_xml.set("xyz", " ".join([str(p) for p in value.value]))
        else:
            # Get pose
            pose = np.array(value)
            if pose.ndim == 1:
                pos = pose[:3]
                origin_xml.set("xyz", " ".join([str(p) for p in pos]))
            elif len(value) == 2:
                pos, rpy = pose[0], self.__convert_angles(pose[1])
                origin_xml.set("xyz", " ".join([str(p) for p in pos]))
                origin_xml.set("rpy", " ".join([str(r) for r in rpy]))
        return origin_xml

    def __setup_revolute_joint(self, joint_xml, j):
        # Add limit
        limit_xml = etree.Element("limit")
        limit = j["limit"].value
        limit_xml.set("lower", str(self.__convert_angles(limit["lower"].value)))
        limit_xml.set("upper", str(self.__convert_angles(limit["upper"].value)))
        limit_xml.set("effort", str(limit["effort"].value))
        limit_xml.set("velocity", str(limit["velocity"].value))
        joint_xml.append(limit_xml)

    def __add_joints(self, root):
        # Elements
        # Operations
        if self.op_joint is None:
            self.op_joint = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                QueryIsStereotypeOperation, "joint_stereotype", 0,
                stereotype=self.joint_element
            )
        res_joint = self.op_joint(root)
        # Add joints
        for j in res_joint:
            j: HyperEdge
            # Generate permutation pairs of joints: all out relations to incoming relations
            permutations = list(j.directed_relation_permutation_with_condition(
                lambda x: self.link_element in x.target.stereotype or self.frame_element in x.target.stereotype)
            )
            for parent, child in permutations:
                # Create joint element
                joint_xml = etree.Element("joint")
                if self.rev_joint in j.stereotype:
                    joint_xml.set("type", "revolute")
                    self.__setup_revolute_joint(joint_xml, j)
                elif self.fixed_joint in j.stereotype:
                    joint_xml.set("type", "fixed")
                elif self.conti_joint in j.stereotype:
                    joint_xml.set("type", "continuous")
                # Add parent
                parent_xml = etree.Element("parent")
                parent_xml.set("link", parent.target.name)
                joint_xml.append(parent_xml)
                # Add child
                child_xml = etree.Element("child")
                child_xml.set("link", child.target.name)
                joint_xml.append(child_xml)
                origin_xml = self.__create_origin(child.value)
                joint_xml.append(origin_xml)
                # Add axis
                axis_xml = self.__add_axis(j, self.axis_element)
                joint_xml.append(axis_xml)
                # Add name to element
                if len(permutations) == 1:
                    joint_xml.set("name", j.name)
                else:
                    joint_xml.set("name", f"{j.name}_{parent.name}_{child.name}")
                # Add joint to robot
                self.robot_root_xml.append(joint_xml)

    def __add_sensors(self, root):
        # Get topic elements
        sensor_mapping = dict()
        sensor_element = self._kinematics_meta["elements"]["sensor"]
        for topic in root.get_children(lambda x: self._communications_meta["topic"] in x.stereotype):
            for _sensor in filter(lambda x: sensor_element in x.target.stereotype, topic.out_relations()):
                sensor: HyperVertex = _sensor.target
                sensor_mapping[sensor] = topic
        #

        sensor_connection_element = self._kinematics_meta["sensors"]["sensor_connection"]
        op_sensor = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "sensor_stereotype", 0,
            sensor_connection_element
        )
        res_sensor_connection = op_sensor(sensor_connection_element, root)
        # Sensor plugin
        sensor_plugin_flag = False
        # Camera
        camera_element = self._kinematics_meta["sensors"]["rgb_camera"]
        # Scanner
        laser_scanner_element = self._kinematics_meta["sensors"]["laser_scanner"]
        for sensor_connection in res_sensor_connection:
            for _link_arc in filter(lambda x: self.link_element in x.target.stereotype, sensor_connection.out_relations()):
                link: HyperVertex = _link_arc.target
                reference_xml = etree.Element("gazebo")
                reference_xml.set("reference", link.name)
                # Add sensors
                for _sensor_arc in filter(lambda x: sensor_element in x.target.stereotype, sensor_connection.in_relations()):
                    if not sensor_plugin_flag:
                        gazebo_element = etree.Element("gazebo")
                        sensor_plugin_element = etree.Element("plugin")
                        # Set filename
                        sensor_plugin_element.set("filename", "gz-sim-sensors-system")
                        # Name
                        sensor_plugin_element.set("name", "gz::sim::systems::Sensors")
                        # Set render engine as a separate element
                        render_engine = etree.Element("render_engine")
                        render_engine.text = "ogre"
                        sensor_plugin_element.append(render_engine)
                        # Add plugin to gazebo
                        gazebo_element.append(sensor_plugin_element)
                        self.robot_root_xml.append(gazebo_element)
                        # Ensure it is only added once
                        sensor_plugin_flag = True
                    #
                    sensor: HyperVertex = _sensor_arc.target
                    sensor_xml = etree.Element("sensor")
                    sensor_xml.set("name", sensor.name)
                    sensor_type = sensor["type"].value
                    sensor_xml.set("type", sensor_type)
                    # Add sensor-specific parameters
                    # Add camera
                    if camera_element in sensor.stereotype:
                        camera_xml = self._camera_elements.setup_camera_elements(sensor)
                        sensor_xml.append(camera_xml)
                    # Add laser scanner
                    elif laser_scanner_element in sensor.stereotype:
                        ray_xml = etree.Element("ray")
                        scan_xml = etree.Element("scan")
                        horizontal_xml = etree.Element("horizontal")
                        # Add horizontal values as text elements
                        samples_xml = etree.Element("samples")
                        samples_xml.text = str(sensor["samples"].value)
                        horizontal_xml.append(samples_xml)
                        resolution_xml = etree.Element("resolution")
                        resolution_xml.text = str(sensor["resolution"].value)
                        horizontal_xml.append(resolution_xml)
                        angles = sensor["angle"].value
                        min_angle_xml = etree.Element("min_angle")
                        min_angle_xml.text = str(self.__convert_angles(angles[0]))
                        horizontal_xml.append(min_angle_xml)
                        max_angle_xml = etree.Element("max_angle")
                        max_angle_xml.text = str(self.__convert_angles(angles[1]))
                        horizontal_xml.append(max_angle_xml)
                        # Setup vertical
                        vertical_xml = etree.Element("vertical")
                        samples_xml = etree.Element("samples")
                        samples_xml.text = str(1)
                        vertical_xml.append(samples_xml)
                        resolution_xml = etree.Element("resolution")
                        resolution_xml.text = str(0.01)
                        vertical_xml.append(resolution_xml)
                        min_angle_xml = etree.Element("min_angle")
                        min_angle_xml.text = str(0)
                        vertical_xml.append(min_angle_xml)
                        max_angle_xml = etree.Element("max_angle")
                        max_angle_xml.text = str(0)
                        vertical_xml.append(max_angle_xml)
                        # Add horizontal
                        scan_xml.append(horizontal_xml)
                        # Add vertical
                        scan_xml.append(vertical_xml)
                        # Add scan
                        ray_xml.append(scan_xml)
                        # Add range
                        range_xml = etree.Element("range")
                        range_values = sensor["range"].value
                        # Minimal range
                        min_range_xml = etree.Element("min")
                        min_range_xml.text = str(range_values[0])
                        range_xml.append(min_range_xml)
                        # Maximal range
                        max_range_xml = etree.Element("max")
                        max_range_xml.text = str(range_values[1])
                        range_xml.append(max_range_xml)
                        # Add resolution
                        resolution_xml = etree.Element("resolution")
                        resolution_xml.text = str(sensor["range_resolution"].value)
                        range_xml.append(resolution_xml)
                        # Add range to ray
                        ray_xml.append(range_xml)

                        # Wrapup
                        sensor_xml.append(ray_xml)
                    # Update rate
                    update_rate_element = etree.Element("update_rate")
                    update_rate_element.text = str(sensor["update_rate"].value)
                    sensor_xml.append(update_rate_element)
                    # Always on
                    always_on_element = etree.Element("always_on")
                    always_on_element.text = str(int(sensor["always_on"].value))
                    sensor_xml.append(always_on_element)
                    # Visualize
                    visualize_element = etree.Element("visualize")
                    visualize_element.text = "true"
                    sensor_xml.append(visualize_element)
                    # Get topics
                    if sensor in sensor_mapping:
                        for _topic_definition in filter(lambda x: x.target.stereotype, sensor_mapping[sensor].in_relations()):
                            topic_definition: HyperVertex = _topic_definition.target
                            topic_element = etree.Element("topic")
                            topic_element.text = '/'.join([root.name, topic_definition["topic_name"].value])
                            sensor_xml.append(topic_element)
                    reference_xml.append(sensor_xml)

                self.robot_root_xml.append(reference_xml)

    def __setup_sim_plugin(self, plugin: HyperEdge):
        gazebo_element = etree.Element("gazebo")
        ros2_control_plugin_element = etree.Element("plugin")
        ros2_control_plugin_element.set("name", plugin["plugin"].value)
        ros2_control_plugin_element.set("filename", plugin["filename"].value)
        parameters = etree.Element("parameters")
        # Add parameters as text element
        self._control_param_path = plugin["parameters"].value
        parameters.text = self.control_param_path
        ros2_control_plugin_element.append(parameters)
        ros2_control_plugin_element.append(parameters)
        gazebo_element.append(ros2_control_plugin_element)
        self.robot_root_xml.append(gazebo_element)

    def __setup_control_interface(self, control_edge: HyperEdge, joint_xml):
        if isinstance(control_edge, HyperEdge):
            for st in control_edge.stereotype.leaf_stereotypes:
                for control_interface in st.in_vertices():
                    el = etree.Element("command_interface")
                    el.set("name", control_interface.name)
                    joint_xml.append(el)
                for state_interface in st.out_vertices():
                    el = etree.Element("state_interface")
                    el.set("name", state_interface.name)
                    joint_xml.append(el)


    def __add_controls(self, root: HyperVertex):
        sim_plugin = None
        if "sim_plugin" in self._kinematics_meta:
            sim_plugin = self._kinematics_meta["sim_plugin"]

        control_element = self._kinematics_meta["elements"]["control"]
        op_control = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "control_stereotype", 0,
            control_element
        )
        res_control = op_control(control_element, root)
        ros2_control_element = None
        control_plugin = self._kinematics_meta["control_plugin"]
        # get joints
        if sim_plugin is not None:
            for plugin in root.get_children(lambda x: sim_plugin in x.stereotype):
                self.__setup_sim_plugin(plugin)
        for plugin in root.get_children(lambda x: control_plugin in x.stereotype):
            plugin: HyperEdge
            control_xml = etree.Element("ros2_control")
            control_xml.set("name", plugin.name)
            control_xml.set("type", "system")
            # Add GazeboSimSystem
            hardware_sim = etree.Element("hardware")
            # Add plugin
            hardware_plugin = etree.Element("plugin")
            hardware_plugin.text =  plugin["plugin"].value
            hardware_sim.append(hardware_plugin)
            control_xml.append(hardware_sim)
            # Add joints
            for _j in filter(lambda x: self.joint_element in x.target.stereotype, plugin.out_relations()):
                j: HyperEdge = _j.target
                if self.fixed_joint in j.stereotype.leaf_stereotypes:
                    continue
                joint_xml = etree.Element("joint")
                joint_xml.set("name", j.name)
                control_xml.append(joint_xml)
                if "control" in j:
                    control_edge = j["control"]
                    self.__setup_control_interface(control_edge, joint_xml)
                # Command interface
                # Position interface
            self.robot_root_xml.append(control_xml)



    def operate(self, *args, **kwargs):
        if self._kinematics_meta is None:
            raise ValueError("Kinematics meta is not defined")
        root = args[0]
        self.robot_root_xml.set("name", root.name)
        self.__add_links(root )
        self.__add_joints(root)
        self.__add_controls(root)
        self.__add_sensors(root)
        return self.robot_root_xml


