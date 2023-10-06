import os
import time
import typing

import lxml
from lxml import objectify

from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.factories.creation_elements import FactoryHypergraphElements
from himeko_hypergraph.src.mapping.bijective_mapping import bijective_mapping
from himeko_hypergraph.src.progeny.geometry.geometry import VisualGeometry, CollisionGeometry, Mesh
from himeko_hypergraph.src.progeny.robotics.elements import RobotNode
from himeko_hypergraph.src.progeny.robotics.kinematics import KinematicLink, KinematicJoint


class ParserUrdf(object):

    def __init__(self) -> None:
        super().__init__()

    def get_geometry(self, node, item, t0: int):
        for geom in item.iterchildren(tag='geometry'):
            _el = geom.getchildren()[0]
            match _el.tag:
                case 'mesh':
                    _geom = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                        Mesh, "geom", t0, node)
                    _geom["filename"] = _el.attrib["filename"]
                case 'box':
                    print('box')

    def get_links(self, robot_node: HyperVertex, robot_item, t0: int):
        for link in robot_item.iterchildren(tag='link'):
            _l = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                KinematicLink, f"{link.attrib['name']}", t0, robot_node)
            _l["name"] = link.attrib["name"]
            for i, visual in enumerate(link.iterchildren(tag='visual')):
                _v = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                    VisualGeometry, f"viz_{link.attrib['name']}_{i}", t0, _l
                )
                self.get_geometry(_v, visual, t0)
            for i, collision in enumerate(link.iterchildren(tag='collision')):
                _c = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                    CollisionGeometry, f"coll_{link.attrib['name']}_{i}", t0, _l
                )
                self.get_geometry(_c, collision, t0)

    def get_joints(self, robot_node: HyperVertex, robot_item, t0: int):
        for joint in robot_item.iterchildren(tag='joint'):
            parent_name = joint.parent.attrib["link"]
            parent_node = next(robot_node.get_children(lambda x, p_name=parent_name: x['name'] == p_name))
            child_name = joint.child.attrib["link"]
            child_node = next(robot_node.get_children(lambda x, p_name=child_name: x['name'] == p_name))
            _j = bijective_mapping(KinematicJoint, f"{joint.attrib['name']}", t0, parent_node, child_node, robot_node)
            _j["name"] = joint.attrib["name"]

    def convert(self, p: os.PathLike | str, parent: typing.Optional[HyperVertex] = None) -> RobotNode:
        robot = objectify.parse(open(p)).getroot()
        robot_name = robot.attrib["name"]
        t0 = time.time_ns()
        robot_node = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            RobotNode, robot_name, t0, parent
        )
        robot_node["name"] = robot_name
        self.get_links(robot_node, robot, t0)
        self.get_joints(robot_node, robot, t0)

        return robot_node



