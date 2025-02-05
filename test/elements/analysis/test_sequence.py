import unittest
from himeko.hbcm.elements.edge import EnumHyperarcDirection
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements

import networkx as nx
import matplotlib.pyplot as plt
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestEdgeCreation(unittest.TestCase):

    def setUp(self):
        logger.info("START: setUp")

    def tearDown(self):
        logger.info("END: tearDown")

    def test_sequence_generation_example(self):
        logger.info("START: test_sequence_generation_example")
        #
        vparent = FactoryHypergraphElements.create_vertex_default(
            "domain", 0)
        nameset = {"v0", "v1", "v2", "v3", "v4", "v5"}
        name_list = list(nameset)
        vertex_dict = {}
        for vname in nameset:
            v = FactoryHypergraphElements.create_vertex_default(
                vname, 0, vparent)
            vertex_dict[vname] = v
        enames = {"e0", "e1", "e2", "e3", "e4"}
        edge_dict = {}
        for ename in enames:
            e = FactoryHypergraphElements.create_edge_default(
                ename, 0, vparent)
            edge_dict[ename] = e
        # Edge 0
        edge_dict["e0"] += (vertex_dict["v0"], EnumHyperarcDirection.UNDEFINED, 10)
        edge_dict["e0"] += (vertex_dict["v3"], EnumHyperarcDirection.UNDEFINED, 10)
        # Edge 1
        edge_dict["e1"] += (vertex_dict["v1"], EnumHyperarcDirection.UNDEFINED, 10)
        edge_dict["e1"] += (vertex_dict["v3"], EnumHyperarcDirection.UNDEFINED, 10)
        # Edge 2
        edge_dict["e2"] += (vertex_dict["v2"], EnumHyperarcDirection.UNDEFINED, 10)
        edge_dict["e2"] += (vertex_dict["v3"], EnumHyperarcDirection.UNDEFINED, 10)
        # Edge 3
        edge_dict["e3"] += (vertex_dict["v4"], EnumHyperarcDirection.UNDEFINED, 10)
        edge_dict["e3"] += (vertex_dict["v3"], EnumHyperarcDirection.UNDEFINED, 10)
        # Edge 4
        edge_dict["e4"] += (vertex_dict["v4"], EnumHyperarcDirection.UNDEFINED, 10)
        edge_dict["e4"] += (vertex_dict["v5"], EnumHyperarcDirection.UNDEFINED, 10)
        # Draw network
        G = nx.Graph()
        G.add_nodes_from(vertex_dict.keys())
        for e in edge_dict.values():
            edge_ = []
            for v in e.out_vertices():
                v: HyperVertex
                edge_.append(v.name)
            G.add_edge(edge_[0], edge_[1])
        #
        logger.info("END: test_sequence_generation_example")


if __name__ == '__main__':
    unittest.main()
