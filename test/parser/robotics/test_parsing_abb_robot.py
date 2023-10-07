from himeko_hypergraph.src.parser.robotics.urdf_parser import ParserUrdf
from himeko_hypergraph.src.progeny.geometry.geometry import MeshVertex
from himeko_hypergraph.src.progeny.robotics.kinematics import KinematicLink, KinematicJoint
from himeko_hypergraph.src.visualization.network_visualization import visualize_node


def test_abb_parsing_visualize_abb():
    p = ParserUrdf()
    robot = p.convert("../../../resources/robots/manipulators/irb2400.urdf")
    visualize_node(robot)

def test_abb_2_visualize_():
    p = ParserUrdf()
    robot = p.convert("../../../resources/robots/manipulators/irb5400.urdf")
    visualize_node(robot)

def test_abb_parsing_get_children():
    p = ParserUrdf()
    robot = p.convert("../../../resources/robots/manipulators/irb2400.urdf")
    assert robot["name"] == "abb_irb2400"
    for l in robot.links:
        print(l["name"])
    for l in robot.joints:
        print(l["name"])
    unique_files = set()
    assert len(unique_files) == 0


def test_abb2_parsing_get_children():
    p = ParserUrdf()
    robot = p.convert("../../../resources/robots/manipulators/irb5400.urdf")
    assert robot["name"] == "abb_irb5400"
    for l in robot.links:
        print(l["name"])
    for l in robot.joints:
        print(l["name"])
    unique_files = set()
    for l in robot.get_children(lambda x: isinstance(x, MeshVertex)):
        unique_files.add(l["filename"])
    assert len(unique_files) == 0

def test_abb_get_mesh_filenames():
    p = ParserUrdf()
    robot = p.convert("../../../resources/robots/manipulators/irb2400.urdf")
    unique_files = set()
    for mesh in robot.get_subelements(lambda x: isinstance(x, MeshVertex)):
        unique_files.add(mesh["filename"])
    print(unique_files)
    assert len(unique_files) == 14
