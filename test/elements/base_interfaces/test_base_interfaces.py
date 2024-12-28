import unittest
from unittest.mock import MagicMock
from himeko_hypergraph.src.himeko.hbcm.elements.interfaces.base_interfaces import IComposable

class TestIComposable(unittest.TestCase):

    def setUp(self):
        self.composable = MagicMock(spec=IComposable)

    def test_add_element(self):
        element = MagicMock()
        self.composable.add_element(element)
        self.composable.add_element.assert_called_with(element)

    def test_remove_element(self):
        element = MagicMock()
        self.composable.remove_element(element)
        self.composable.remove_element.assert_called_with(element)

    def test_update_element(self):
        element = MagicMock()
        self.composable.update_element(element)
        self.composable.update_element.assert_called_with(element)

    def test_get_element(self):
        key = 'test_key'
        self.composable.get_element(key)
        self.composable.get_element.assert_called_with(key)

    def test_get_children(self):
        condition = MagicMock()
        depth = 2
        self.composable.get_children(condition, depth)
        self.composable.get_children.assert_called_with(condition, depth)

    def test_get_all_children(self):
        condition = MagicMock()
        self.composable.get_all_children(condition)
        self.composable.get_all_children.assert_called_with(condition)

    def test_get_leaf_elements(self):
        self.composable.get_leaf_elements()
        self.composable.get_leaf_elements.assert_called()

    def test_get_parent(self):
        self.composable.get_parent()
        self.composable.get_parent.assert_called()

    def test_get_siblings(self):
        f = MagicMock()
        self.composable.get_siblings(f)
        self.composable.get_siblings.assert_called_with(f)

if __name__ == '__main__':
    unittest.main()