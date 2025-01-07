from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge

from lxml import etree
import numpy as np

from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation


class TransformationUrdf(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        # Kinematics meta data check
        if kinematics_meta is None:
            raise ValueError("Kinematics meta is required")
        self._kinematics_meta = kinematics_meta
        self.__setup_kinematics_element()


    def __setup_kinematics_element(self):
        self.robot_root_xml = etree.Element("robot")
        # Set up stereotypes
        self.geom_box = self._kinematics_meta["geometry"]["box"]
        self.geom_cylinder = self._kinematics_meta["geometry"]["cylinder"]
        self.geom_sphere = self._kinematics_meta["geometry"]["sphere"]
        # Axis
        self.axis_element = self._kinematics_meta["axes"]["axis_definition"]
        # Link and frame
        self.link_element = self._kinematics_meta["elements"]["link"]
        self.frame_element = self._kinematics_meta["elements"]["frame"]
        # Joints
        self.joint_element = self._kinematics_meta["elements"]["joint"]
        self.rev_joint = self._kinematics_meta["rev_joint"]
        self.fixed_joint = self._kinematics_meta["fixed_joint"]
        # Angle
        self.angle_unit = self._kinematics_meta["units"]["angle"].value
        # Operate joint stereotype
        self.op_joint = None

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
        match self.angle_unit:
            case "radian":
                return angles
            case "degree":
                return np.deg2rad(angles)
            case _:
                raise ValueError("Unknown angle")

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
        limit_xml.set("lower", str(limit["lower"].value))
        limit_xml.set("upper", str(limit["upper"].value))
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
        sensor_element = self["kinematics_meta"]["elements"]["sensor"]
        op_sensor = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "sensor_stereotype", 0,
            sensor_element
        )
        res_sensor = op_sensor(root)
        for sensor in res_sensor:
            sensor_xml = etree.Element("sensor")
            sensor_xml.set("name", sensor.name)
            sensor_type = sensor["type"].value
            sensor_xml.set("type", sensor_type)
            # Add sensor-specific parameters
            for param in sensor["parameters"].value:
                param_xml = etree.Element(param["name"].value)
                param_xml.set("value", str(param["value"].value))
                sensor_xml.append(param_xml)
            self.robot_root_xml.append(sensor_xml)

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
                gazebo_element = etree.Element("gazebo")
                ros2_control_plugin_element = etree.Element("plugin")
                ros2_control_plugin_element.set("name", plugin["plugin"].value)
                ros2_control_plugin_element.set("filename", plugin["filename"].value)
                parameters = etree.Element("parameters")
                # Add parameters as text element
                parameters.text = plugin["parameters"].value
                ros2_control_plugin_element.append(parameters)
                ros2_control_plugin_element.append(parameters)
                gazebo_element.append(ros2_control_plugin_element)
                self.robot_root_xml.append(gazebo_element)

        for plugin in root.get_children(lambda x: control_plugin in x.stereotype.leaf_stereotypes):
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
        return self.robot_root_xml


