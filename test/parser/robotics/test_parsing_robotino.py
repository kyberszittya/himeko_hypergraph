from himeko_hypergraph.src.parser.robotics.urdf_parser import ParserUrdf
import yaml

from himeko_hypergraph.src.progeny.geometry.geometry import Mesh
from himeko_hypergraph.src.progeny.robotics.kinematics import KinematicLink, KinematicJoint
from himeko_hypergraph.src.visualization.network_visualization import visualize_node


def test_robotino_parsing():
    p = ParserUrdf()
    with open("../../../resources/commercial/robotino_param.yaml") as f:
        params = yaml.safe_load(f)
    robot = p.convert("../../../resources/commercial/robotino.urdf")
    assert robot["name"] == "robotino"
    for l in robot.get_subelements(lambda x: isinstance(x, KinematicLink)):
        print(l["name"])
    for l in robot.get_subelements(lambda x: isinstance(x, KinematicJoint)):
        print(l["name"])
    assert len(list(robot.get_subelements(lambda x: isinstance(x, KinematicLink)))) == \
           params['robotino_kinematics']['CNT_ROBOTINO_LINK']
    assert len(list(robot.get_subelements(lambda x: isinstance(x, KinematicJoint)))) == \
           params['robotino_kinematics']['CNT_ROBOTINO_JOINT']
    unique_files = set()
    for l in robot.get_subelements(lambda x: isinstance(x, Mesh)):
        unique_files.add(l["filename"])
    assert len(unique_files) == 3


def test_robotino_parsing_get_children():
    p = ParserUrdf()
    with open("../../../resources/commercial/robotino_param.yaml") as f:
        params = yaml.safe_load(f)
    robot = p.convert("../../../resources/commercial/robotino.urdf")
    assert robot["name"] == "robotino"
    for l in robot.get_children(lambda x: isinstance(x, KinematicLink)):
        print(l["name"])
    for l in robot.get_children(lambda x: isinstance(x, KinematicJoint)):
        print(l["name"])
    assert len(list(robot.get_children(lambda x: isinstance(x, KinematicLink)))) == \
           params['robotino_kinematics']['CNT_ROBOTINO_LINK']
    assert len(list(robot.get_children(lambda x: isinstance(x, KinematicJoint)))) == \
           params['robotino_kinematics']['CNT_ROBOTINO_JOINT']
    unique_files = set()
    for l in robot.get_children(lambda x: isinstance(x, Mesh)):
        unique_files.add(l["filename"])
    assert len(unique_files) == 0


def test_robotino_parsing_visualize():
    p = ParserUrdf()
    robot = p.convert("../../../resources/commercial/robotino.urdf")
    visualize_node(robot)


