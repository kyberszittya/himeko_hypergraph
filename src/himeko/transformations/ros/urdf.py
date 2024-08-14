from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge

from lxml import etree


from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation


class TransformationUrdf(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, kinematics_meta=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self._named_attr["kinematics_meta"] = kinematics_meta
        self.robot_root_xml = etree.Element("robot")


    def __add_links(self, root):
        # Geometry
        _box = self["kinematics_meta"]["geometry"]["box"]
        _cylinder = self["kinematics_meta"]["geometry"]["cylinder"]
        _sphere = self["kinematics_meta"]["geometry"]["sphere"]
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
            # Create geometry element
            geometry_xml = etree.Element("geometry")
            # Add geometry to visual
            visual_xml.append(geometry_xml)
            # Check for different geometries
            if _cylinder in _visual.value.stereotype:
                # Add cylinder
                cylinder_xml = etree.Element("cylinder")
                length, radius = _visual.value["dimension"].value
                cylinder_xml.set("length", str(length))
                cylinder_xml.set("radius", str(radius))
                # Add to visual
                geometry_xml.append(cylinder_xml)
            elif _box in _visual.value.stereotype:
                # Add box
                box_xml = etree.Element("box")
                size = _visual.value["dimension"].value
                box_xml.set("size", " ".join([str(s) for s in size]))
                # Add to visual
                geometry_xml.append(box_xml)
            elif _sphere in _visual.value.stereotype:
                # Add sphere
                sphere_xml = etree.Element("sphere")
                radius = _visual.value["dimension"].value
                sphere_xml.set("radius", str(radius))
                # Add to visual
                geometry_xml.append(sphere_xml)

    def __add_joints(self, root):
        joint_element = self["kinematics_meta"]["elements"]["joint"]
        rev_joint = self["kinematics_meta"]["rev_joint"]
        op_joint = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "joint_stereotype", 0,
            stereotype=joint_element
        )
        res_joint = op_joint(root)
        # Add joints
        for j in res_joint:
            joint_xml = etree.Element("joint")
            joint_xml.set("name", j.name)
            if rev_joint in j.stereotype:
                joint_xml.set("type", "revolute")
            # Add parent
            # Add child
            # Add origin
            # Add axis
            # Add limit
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


