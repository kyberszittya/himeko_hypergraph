import unittest
import os

from himeko.hbcm.parser.robotics.urdf_parser import ParserUrdf
from himeko.hbcm.progeny.geometry.nodes import BoxPrimitiveVertex


class TestParserSimplePrimitives(unittest.TestCase):

    def setUp(self):
        # Add to detect if the test is run in the test folder or in the root folder

        if os.path.basename(os.getcwd())     == "test":
            self.pwd_path = "../resources/robots/mobile/"
        else:
            self.pwd_path = "resources/robots/mobile/"
        self.cube_file = os.path.join(self.pwd_path, "cube_robot.urdf")
        self.ellipsoid_file = os.path.join(self.pwd_path, "ellipsoid_robot.urdf")
        self.parser = ParserUrdf()

    def test_simple_cube_parsing(self):
        robot = self.parser.convert(self.cube_file)
        self.assertEqual(robot["name"], "cube_robot")
        for l in robot.links:
            print(l["name"])
        links = set([
            "base_link"
        ])

        # Check if all links are present
        for l in robot.links:
            self.assertIn(l["name"], links)
        # Select base_link
        base_link = robot["base_link"]
        # Get visual elements and geometries
        box = list(base_link.get_children(lambda x: isinstance(x, BoxPrimitiveVertex), None))
        # Ensure that there are two box geometries
        self.assertEqual(len(box), 2)
        # Check if each element's parent is not the base_link
        for b in box:
            self.assertNotEqual(b.get_parent(), base_link)
        # Check if dimensions are correct
        for b in box:
            b["size"] = [1.0, 1.0, 1.0]

