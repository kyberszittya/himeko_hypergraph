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
        self._named_attr["kinematics_meta"] = kinematics_meta
        self.robot_root_xml = etree.Element("robot")

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
            self["kinematics_meta"]["geometry"]["box"],
            self["kinematics_meta"]["geometry"]["cylinder"],
            self["kinematics_meta"]["geometry"]["sphere"]
        ]
        # Get link element
        link_element = self["kinematics_meta"]["elements"]["link"]
        op = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "link_stereotype", 0,
            link_element
        )
        res = op(link_element, root, depth=None)
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
                # Create root element
                el_root_origin = self.__create_origin(root_origin)
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
                inertia_xml.append(el_root_origin)
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

        if "radian" == self["kinematics_meta"]["units"]["angle"].value:
            return angles
        elif "degree" == self["kinematics_meta"]["units"]["angle"].value:
            return np.deg2rad(angles)
        else:
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

    def __add_joints(self, root):
        # Elements
        # Geometric elements
        link_element = self["kinematics_meta"]["elements"]["link"]
        joint_element = self["kinematics_meta"]["elements"]["joint"]
        rev_joint = self["kinematics_meta"]["rev_joint"]
        axis_element = self["kinematics_meta"]["axes"]["axis_definition"]
        # Operations
        op_joint = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "joint_stereotype", 0,
            stereotype=joint_element
        )
        res_joint = op_joint(root)
        # Add joints
        for j in res_joint:
            j: HyperEdge
            # Generate permutation pairs of joints: all out relations to incoming relations
            permutations = list(j.directed_relation_permutation_with_condition(
                lambda x: link_element in x.target.stereotype)
            )
            for parent, child in permutations:
                # Create joint element
                joint_xml = etree.Element("joint")
                if rev_joint in j.stereotype:
                    joint_xml.set("type", "revolute")
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
                axis_xml = self.__add_axis(j, axis_element)
                joint_xml.append(axis_xml)
                # Add limit
                limit_xml = etree.Element("limit")
                limit = j["limit"].value
                limit_xml.set("lower", str(limit["lower"].value))
                limit_xml.set("upper", str(limit["upper"].value))
                limit_xml.set("effort", str(limit["effort"].value))
                limit_xml.set("velocity", str(limit["velocity"].value))
                joint_xml.append(limit_xml)
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

    def __add_controls(self, root):
        control_element = self["kinematics_meta"]["elements"]["control"]
        op_control = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "control_stereotype", 0,
            control_element
        )
        res_control = op_control(root)
        for control in res_control:
            control_xml = etree.Element("control")
            control_xml.set("name", control.name)
            control_type = control["type"].value
            control_xml.set("type", control_type)
            # Add control-specific parameters
            for param in control["parameters"].value:
                param_xml = etree.Element(param["name"].value)
                param_xml.set("value", str(param["value"].value))
                control_xml.append(param_xml)
            self.robot_root_xml.append(control_xml)

    def operate(self, *args, **kwargs):
        if self._named_attr["kinematics_meta"] is None:
            raise ValueError("Kinematics meta is not defined")
        root = args[0]
        self.robot_root_xml.set("name", root.name)
        self.__add_links(root )
        self.__add_joints(root)
        return self.robot_root_xml


