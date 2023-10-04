import os
import time

import lxml
from lxml import objectify

from himeko_hypergraph.src.elements.vertex import HyperVertex
from himeko_hypergraph.src.factories.creation_elements import FactoryHypergraphElements
from himeko_hypergraph.src.progeny.geometry.geometry import VisualGeometry, CollisionGeometry
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
                        KinematicLink, "geom", t0, node)
                case 'box':
                    print('box')

    def get_links(self, robot_node: HyperVertex, robot_item, t0: int):
        for link in robot_item.iterchildren(tag='link'):
            _l = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                KinematicLink, f"{link.attrib['name']}", t0, robot_node)
            for visual in link.iterchildren(tag='visual'):
                _v = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                    VisualGeometry, f"{link.attrib['name']}", t0, _l
                )
                self.get_geometry(_v, visual, t0)
            for collision in link.iterchildren(tag='collision'):
                _c = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                    CollisionGeometry, f"{link.attrib['name']}", t0, _l
                )
                self.get_geometry(_c, collision, t0)

    def get_joints(self, robot_node: HyperVertex, robot_item, t0: int):
        for joint in robot_item.iterchildren(tag='joint'):
            _j = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
                KinematicJoint, f"{joint.attrib['name']}", t0, robot_node
            )
            _j["name"] = joint.attrib["name"]


    def convert(self, p: os.PathLike):
        robot = objectify.parse(open(p)).getroot()
        robot_name = robot.attrib["name"]
        t0 = time.time_ns()
        robot_node = FactoryHypergraphElements.create_vertex_default(robot_name, t0)
        self.get_links(robot_node, robot, t0)
        self.get_joints(robot_node, robot, t0)


def main():
    p = ParserUrdf()
    p.convert("../../../resources/commercial/robotino.urdf")


if __name__ == "__main__":
    main()
