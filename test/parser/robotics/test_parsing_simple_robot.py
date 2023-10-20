from himeko_hypergraph.src.parser.robotics.urdf_parser import ParserUrdf
from himeko_hypergraph.src.visualization.network_visualization import visualize_node


def test_simple_robot():
    p = ParserUrdf()
    robot = p.convert("../../../resources/robots/mobile/simple_robot.urdf")
    visualize_node(robot)
