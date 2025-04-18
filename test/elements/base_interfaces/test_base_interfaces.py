import unittest
from unittest.mock import MagicMock
import logging

from himeko.hbcm.elements.interfaces.base_interfaces import IComposable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestIComposable(unittest.TestCase):

    def setUp(self):
        self.composable = MagicMock(spec=IComposable)
        # Logging
        logger.info("START: setUp")

    def tearDown(self):
        # Logging
        logger.info("END: tearDown")

    def test_add_element(self):
        logger.info("START: test_add_element")
        #
        element = MagicMock()
        self.composable.add_element(element)
        self.composable.add_element.assert_called_with(element)
        #
        logger.info("END: test_add_element")

    def test_remove_element(self):
        logger.info("START: test_remove_element")
        #
        element = MagicMock()
        self.composable.remove_element(element)
        self.composable.remove_element.assert_called_with(element)
        #
        logger.info("END: test_remove_element")

    def test_update_element(self):
        logger.info("START: test_update_element")
        #
        element = MagicMock()
        self.composable.update_element(element)
        self.composable.update_element.assert_called_with(element)
        #
        logger.info("END: test_update_element")

    def test_get_element(self):
        logger.info("START: test_get_element")
        #
        key = 'test_key'
        self.composable.get_element(key)
        self.composable.get_element.assert_called_with(key)
        #
        logger.info("END: test_get_element")

    def test_get_children(self):
        logger.info("START: test_get_children")
        #
        condition = MagicMock()
        depth = 2
        self.composable.get_children(condition, depth)
        self.composable.get_children.assert_called_with(condition, depth)
        #
        logger.info("END: test_get_children")

    def test_get_all_children(self):
        logger.info("START: test_get_all_children")
        #
        condition = MagicMock()
        self.composable.get_all_children(condition)
        self.composable.get_all_children.assert_called_with(condition)
        #
        logger.info("END: test_get_all_children")

    def test_get_leaf_elements(self):
        logger.info("START: test_get_leaf_elements")
        #
        self.composable.get_leaf_elements()
        self.composable.get_leaf_elements.assert_called()
        #
        logger.info("END: test_get_leaf_elements")

    def test_get_parent(self):
        logger.info("START: test_get_parent")
        #
        self.composable.get_parent()
        self.composable.get_parent.assert_called()
        #
        logger.info("END: test_get_parent")

    def test_get_siblings(self):
        logger.info("START: test_get_siblings")
        #
        f = MagicMock()
        self.composable.get_siblings(f)
        self.composable.get_siblings.assert_called_with(f)
        #
        logger.info("END: test_get_siblings")


if __name__ == '__main__':
    unittest.main()
