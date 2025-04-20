import unittest
import logging

from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements, create_default_vertex_guid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestHypergraphAttributes(unittest.TestCase):

    def setUp(self):
        # Set up the test case
        logger.info("START: setUp")

    def tearDown(self):
        # Clean up after each test
        logger.info("END: tearDown")

    def test_vertex_attribute_creation(self):
        logger.info("START: test_vertex_creation")
        #
        v0 = FactoryHypergraphElements.create_vertex_default("vertex0", 0, None)
        self.assertEqual(v0.label, "vertex0.0")
        self.assertEqual(v0.guid, create_default_vertex_guid(v0.name, v0.timestamp, None))
        assert v0.suid != v0.guid
        assert v0.name == "vertex0"
        assert v0.serial == 0
        assert v0.timestamp == 0
        # Add attribute
        attr = FactoryHypergraphElements.create_attribute_default("attr0", 678.6, float, 0, v0)
        self.assertEqual(attr.label, "vertex0.0//attr0.0")
        self.assertEqual(attr.value, 678.6)
        #
        logger.info("END: test_attributes_creation")

    def test_vertex_attribute_modification(self):
        def test_vertex_creation(self):
            logger.info("START: test_vertex_creation")
        #
        v0 = FactoryHypergraphElements.create_vertex_default("vertex0", 0, None)
        self.assertEqual(v0.label, "vertex0.0")
        self.assertEqual(v0.guid, create_default_vertex_guid(v0.name, v0.timestamp, None))
        assert v0.suid != v0.guid
        assert v0.name == "vertex0"
        assert v0.serial == 0
        assert v0.timestamp == 0
        # Add attribute
        attr = FactoryHypergraphElements.create_attribute_default("attr0", 678.6, float, 0, v0)
        self.assertEqual(attr.label, "vertex0.0//attr0.0")
        self.assertEqual(attr.value, 678.6)
        # Modify attribute
        attr.value = 123.4
        self.assertEqual(attr.value, 123.4)
        #
        logger.info("END: test_attributes_creation")
