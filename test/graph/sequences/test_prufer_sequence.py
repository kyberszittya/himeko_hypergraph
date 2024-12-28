import unittest
import logging

from himeko.common.clock import NullClock
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements, FactoryHypergraphElementsClock

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestHypergraphSequence(unittest.TestCase):

    def setUp(self):
        # Logging
        logger.info("START: setUp")
        # Factory with null clock
        self.clock = NullClock()
        self.factory = FactoryHypergraphElementsClock(self.clock)

    def tearDown(self):
        # Logging
        logger.info("END: tearDown")

    def test_prufer_sequence(self):
        logger.info("START: test_prufer_sequence")
        #
        # Create a simple hypergraph with nodes (using factory)
        h0: HyperVertex = self.factory.create_vertex("A")
        h1 = self.factory.create_vertex("B", h0)
        h2 = self.factory.create_vertex("C", h0)
        # Add new level
        h3 = self.factory.create_vertex("D", h1)
        h4 = self.factory.create_vertex("E", h1)
        # Another branch
        h5 = self.factory.create_vertex("F", h2)
        # Add branch to "D"
        h6 = self.factory.create_vertex("G", h3)
        # Assert that the hypergraph is not None
        self.assertIsNotNone(h0)
        # Get the children of the root
        children = list(h0.get_all_children(lambda x: True))
        self.assertEqual(len(children), 6)
        # Check Prufer sequence
        sequence = h0.prufer_code
        self.assertEqual(len(sequence), 5)
        # Assert equal to Prüfer sequence
        self.assertListEqual([x.name for x in sequence], ["B","C", "D", "B", "A"])
        #
        logger.info("END: test_prufer_sequence")


if __name__ == '__main__':
    unittest.main()
