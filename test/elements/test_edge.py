import unittest
import logging
from himeko.hbcm.elements.edge import EnumHyperarcDirection
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestEdgeCreation(unittest.TestCase):

    def setUp(self):
        logger.info("START: setUp")

    def tearDown(self):
        logger.info("END: tearDown")

    def test_edge_creation(self):
        logger.info("START: test_edge_creation")
        #
        vparent = FactoryHypergraphElements.create_vertex_default(
            "domain", 0, None)
        nameset = {"v0", "v1"}
        v0 = FactoryHypergraphElements.create_vertex_default(
            "v0", 0, vparent)
        v1 = FactoryHypergraphElements.create_vertex_default(
            "v1", 0, vparent)
        e0 = FactoryHypergraphElements.create_edge_default(
            "e0", 0, vparent)
        e0 += (v0, EnumHyperarcDirection.UNDEFINED, 10)
        e0 += (v1, EnumHyperarcDirection.UNDEFINED, 20)
        assert e0.name == "e0"
        assert e0.label == "domain.0||e0.0.2"
        assert len(e0) == 2
        out_relations = [x for x in e0.out_relations()]
        in_relations = [x for x in e0.in_relations()]
        assert len(out_relations) == len(in_relations)
        for i in e0.out_vertices():
            assert i.name in nameset
        # END
        logger.info("END: test_edge_creation")


if __name__ == '__main__':
    unittest.main()
