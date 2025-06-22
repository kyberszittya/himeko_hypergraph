import unittest
from himeko.hbcm.elements.element import HypergraphElement

class TestSetParent(unittest.TestCase):
    def setUp(self):
        # Create a simple tree: root -> child1 -> child2
        self.root = HypergraphElement("root", 0, 0, b"r", b"r", "root")
        self.child1 = HypergraphElement("child1", 0, 1, b"c1", b"c1", "child1", parent=self.root)
        self.child2 = HypergraphElement("child2", 0, 2, b"c2", b"c2", "child2", parent=self.child1)
        self.root.add_element(self.child1)
        self.child1.add_element(self.child2)

    def test_set_parent_triggers_recalculation_from_root(self):
        # Save old prufer code for comparison
        old_prufer = self.root.prufer_code
        # Change parent of child1 to None (detach from root)
        self.child1.set_parent(None)
        # Check if child1's parent is now None
        self.assertIsNone(self.child1.parent)
        # Check if child1 is not in root's children anymore
        self.assertNotIn(self.child1, self.root.get_subelements(lambda x: True))
        # After detaching, root and child1 should have different prufer codes
        self.assertNotEqual(self.root.prufer_code, self.child1.prufer_code)
        # Compare with old prufer code
        self.assertNotEqual(old_prufer, self.root.prufer_code)
        # Now reattach child1 to root and check recalculation
        self.child1.set_parent(self.root)
        self.assertEqual(self.child1.parent, self.root)
        # After reattaching, prufer code should be recalculated
        self.assertIsNotNone(self.root.prufer_code)
        self.assertIsNotNone(self.child1.prufer_code)

    def test_set_parent_finds_new_root(self):
        # Add a new root and reparent child1 under it
        new_root = HypergraphElement("new_root", 0, 3, b"nr", b"nr", "new_root")
        new_root.add_element(self.child1)
        self.child1.set_parent(new_root)
        # The root of child2 should now be new_root
        node = self.child2
        while node.parent is not None:
            node = node.parent
        self.assertEqual(node, new_root)

if __name__ == "__main__":
    unittest.main()