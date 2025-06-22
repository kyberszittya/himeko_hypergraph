import unittest
from himeko.hbcm.elements.element import HypergraphElement

class TestHypergraphElementRename(unittest.TestCase):
    def setUp(self):
        self.parent = HypergraphElement("parent", 0, 0, b"p", b"p", "parent")
        self.child = HypergraphElement("child", 0, 1, b"c", b"c", "child", parent=self.parent)
        self.parent.add_element(self.child)

    def test_rename_element(self):
        # Rename the child
        old_name = self.child.name
        new_name = "child_renamed"
        self.child.name = new_name

        # Check the name is updated
        self.assertEqual(self.child.name, new_name)
        # Check parent's index is updated
        self.assertIn(new_name, self.parent._index_named_elements)
        self.assertIs(self.parent._index_named_elements[new_name], self.child)
        # Old name should be removed
        self.assertNotIn(old_name, self.parent._index_named_elements)
        # Check the label is updated
        expected_label = f"{self.parent.label}//{new_name}"

if __name__ == "__main__":
    unittest.main()