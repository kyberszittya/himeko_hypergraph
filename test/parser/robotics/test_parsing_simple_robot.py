import unittest
import os

from himeko.hbcm.parser.robotics.urdf_parser import ParserUrdf
from himeko.hbcm.progeny.geometry.nodes import BoxPrimitiveVertex, SpherePrimitiveVertex, CylinderPrimitiveVertex
from himeko.hbcm.progeny.robotics.kinematics import KinematicLink
from himeko.hbcm.visualization.network_visualization import visualize_node




class TestParserSimpleRobot(unittest.TestCase):

    def setUp(self):
        self.parser = ParserUrdf()
        self.pwd_path = "resources/robots/mobile/"
        self.robot_file = os.path.join(self.pwd_path, "simple_robot.urdf")

    def test_simple_robot_visualization(self):
        robot = self.parser.convert(self.robot_file)
        visualize_node(robot)

    def test_simple_robot_parsing(self):
        robot = self.parser.convert(self.robot_file)
        self.assertEqual(robot["name"], "rb1")
        for l in robot.links:
            print(l["name"])
        for l in robot.joints:
            print(l["name"])
        links = set([
            "base_link",
            "base_footprint",
            "right_wheel",
            "left_wheel",
            "front_caster",
            "back_caster",
            "front_laser"
        ])
        joints = set([
            "joint_base_link_2_right_wheel",
            "joint_base_link_2_left_wheel",
            "joint_base_link_2_front_caster",
            "joint_base_link_2_back_caster",
            "joint_base_link_laser",
            "joint_base_link_2_base_footprint"
        ])
        # Check if all links are present
        for l in robot.links:
            self.assertIn(l["name"], links)
        # Check if all joints are present
        for l in robot.joints:
            self.assertIn(l["name"], joints)
        # Get visual elements and geometries
        cyl = list(robot["base_link"].get_children(lambda x: isinstance(x, CylinderPrimitiveVertex), None))
        self.assertEqual(len(cyl), 2)
        for s in cyl:
            self.assertEqual(s["radius"], [0.25, 0.3])



