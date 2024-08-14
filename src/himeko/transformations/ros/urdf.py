from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge

from lxml import etree
import numpy as np

from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation


class TransformationUrdf(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self._named_attr["kinematics_meta"] = kinematics_meta
        self.robot_root_xml = etree.Element("robot")


    def __generate_geometry(self, geometry, *args):
        _box, _cylinder, _sphere = args
        # Create geometry element
        geometry_xml = etree.Element("geometry")
        # Check for different geometries
        if _cylinder in geometry.value.stereotype:
            # Add cylinder
            cylinder_xml = etree.Element("cylinder")
            length, radius = geometry.value["dimension"].value
            cylinder_xml.set("length", str(length))
            cylinder_xml.set("radius", str(radius))
            # Add to geometry
            geometry_xml.append(cylinder_xml)
        elif _box in geometry.value.stereotype:
            # Add box
            box_xml = etree.Element("box")
            size = geometry.value["dimension"].value
            box_xml.set("size", " ".join([str(s) for s in size]))
            # Add to geoemtry
            geometry_xml.append(box_xml)
        elif _sphere in geometry.value.stereotype:
            # Add sphere
            sphere_xml = etree.Element("sphere")
            radius = geometry.value["dimension"].value[-1]
            sphere_xml.set("radius", str(radius))
            # Add to geometry
            geometry_xml.append(sphere_xml)
        return geometry_xml



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
            # Geometry
            _visual = link["visual"]
            # Create visual element
            visual_xml = etree.Element("visual")
            # Add visual to link
            link_xml.append(visual_xml)
            # Add geometry to visual
            visual_geom = self.__generate_geometry(_visual, *geometries)
            visual_xml.append(visual_geom)
            # Get collision
            _collision = link["collision"]
            # Create collision element
            collision_xml = etree.Element("collision")
            # Add collision to link
            link_xml.append(collision_xml)
            # Add geometry to collision
            collision_geom = self.__generate_geometry(_collision, *geometries)
            collision_xml.append(collision_geom)

    def __add_axis(self, j, axis_element):
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
                # Add origin
                origin_xml = etree.Element("origin")
                # Get pose
                pose = np.array(child.value)
                if pose.ndim == 1:
                    pos = pose[:3]
                    origin_xml.set("xyz", " ".join([str(p) for p in pos]))
                elif len(child.value) == 2:
                    pos, rpy = pose[0], self.__convert_angles(pose[1])
                    origin_xml.set("xyz", " ".join([str(p) for p in pos]))
                    origin_xml.set("rpy", " ".join([str(r) for r in rpy]))
                joint_xml.append(origin_xml)
                # Add axis
                axis_xml = self.__add_axis(j, axis_element)
                joint_xml.append(axis_xml)
                # Add limit
                # Add name to element
                if len(permutations) == 1:
                    joint_xml.set("name", j.name)
                else:
                    joint_xml.set("name", f"{j.name}_{parent.name}_{child.name}")
                # Add joint to robot
                self.robot_root_xml.append(joint_xml)

    def operate(self, *args, **kwargs):
        if self._named_attr["kinematics_meta"] is None:
            raise ValueError("Kinematics meta is not defined")
        root = args[0]
        self.robot_root_xml.set("name", root.name)
        self.__add_links(root )
        self.__add_joints(root)
        return self.robot_root_xml


