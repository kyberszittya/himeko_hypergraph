import unittest
import logging
from himeko.common.clock import NullClock
from himeko.hbcm.elements.edge import EnumHyperarcDirection
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements, FactoryHypergraphElementsClock

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TestFactoryHypergraphElements(unittest.TestCase):

    def setUp(self):
        self.clock = NullClock()
        self.clock.tick()
        logger.info("START: setUp")

    def tearDown(self):
        logger.info("END: tearDown")

    # TEST: Create a vertex with default values
    def test_create_vertex_default(self):
        logger.info("START: test_create_vertex_default")
        vertex = FactoryHypergraphElements.create_vertex_default("A", self.clock.nano_sec)
        self.assertIsNotNone(vertex)
        self.assertEqual(vertex.name, "A")
        self.assertEqual(vertex.timestamp, self.clock.nano_sec)
        logger.info("END: test_create_vertex_default")

    # TEST: Create an edge with default values
    def test_create_edge_default(self):
        logger.info("START: test_create_edge_default")
        vertex1 = FactoryHypergraphElements.create_vertex_default("A", self.clock.nano_sec)
        vertex2 = FactoryHypergraphElements.create_vertex_default("B", self.clock.nano_sec)
        edge = FactoryHypergraphElements.create_edge_default("edge1", self.clock.nano_sec, vertex1)
        # Add hyperarcs
        edge.associate_vertex((vertex1, EnumHyperarcDirection.IN, 1))
        edge.associate_vertex((vertex2, EnumHyperarcDirection.OUT, 1))
        # Assertions
        self.assertIsNotNone(edge)
        self.assertEqual(edge.name, "edge1")
        self.assertEqual(edge.timestamp, self.clock.nano_sec)
        # Check vertices
        self.assertIn(vertex1, edge.in_vertices())
        self.assertIn(vertex2, edge.out_vertices())
        # Check directions
        self.assertEqual(next(edge.out_relations()).direction, EnumHyperarcDirection.OUT)
        self.assertEqual(next(edge.in_relations()).direction, EnumHyperarcDirection.IN)
        logger.info("END: test_create_edge_default")

    # TEST: Create a vertex with default values and attributes
    def test_create_vertex_with_attributes(self):
        logger.info("START: test_create_vertex_with_attributes")
        vertex = FactoryHypergraphElements.create_vertex_default("A", self.clock.nano_sec)
        attribute = FactoryHypergraphElements.create_attribute_default("color", "red", "string",
                                                                       self.clock.nano_sec, vertex)
        vertex.add_element(attribute)
        self.assertIsNotNone(vertex)
        self.assertEqual(vertex.name, "A")
        self.assertEqual(vertex.timestamp, self.clock.nano_sec)
        self.assertEqual(vertex["color"].value, "red")
        logger.info("END: test_create_vertex_with_attributes")


class TestFactoryHypergraphElementsClock(unittest.TestCase):

    def setUp(self):
        self.clock = NullClock()
        self.clock.tick()
        self.factory = FactoryHypergraphElementsClock(self.clock)
        logger.info("START: setUp")

    def tearDown(self):
        logger.info("END: tearDown")

    def test_create_vertex_with_clock(self):
        logger.info("START: test_create_vertex_with_clock")
        vertex = self.factory.create_vertex("A")
        self.assertIsNotNone(vertex)
        self.assertEqual(vertex.name, "A")
        self.assertEqual(vertex.timestamp, self.clock.nano_sec)
        logger.info("END: test_create_vertex_with_clock")

    def test_create_edge_with_clock(self):
        logger.info("START: test_create_edge_with_clock")
        vertex1 = self.factory.create_vertex("A")
        vertex2 = self.factory.create_vertex("B")
        edge = self.factory.create_edge("edge1", vertex1)
        edge.associate_vertex((vertex1, EnumHyperarcDirection.IN, 1))
        edge.associate_vertex((vertex2, EnumHyperarcDirection.OUT, 1))
        self.assertIsNotNone(edge)
        self.assertEqual(edge.name, "edge1")
        self.assertEqual(edge.timestamp, self.clock.nano_sec)
        self.assertIn(vertex1, edge.in_vertices())
        self.assertIn(vertex2, edge.out_vertices())
        self.assertEqual(next(edge.out_relations()).direction, EnumHyperarcDirection.OUT)
        self.assertEqual(next(edge.in_relations()).direction, EnumHyperarcDirection.IN)
        logger.info("END: test_create_edge_with_clock")

    def test_create_vertex_with_attributes_and_clock(self):
        logger.info("START: test_create_vertex_with_attributes_and_clock")
        vertex = self.factory.create_vertex("A")
        attribute = self.factory.create_attribute("color", "red", "string", vertex)
        vertex.add_element(attribute)
        self.assertIsNotNone(vertex)
        self.assertEqual(vertex.name, "A")
        self.assertEqual(vertex.timestamp, self.clock.nano_sec)
        self.assertEqual(vertex["color"].value, "red")
        logger.info("END: test_create_vertex_with_attributes_and_clock")


if __name__ == '__main__':
    unittest.main()