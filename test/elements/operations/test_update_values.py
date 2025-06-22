import unittest
from himeko.hbcm.elements.edge import HyperEdge, EnumHyperarcDirection
from himeko.hbcm.elements.vertex import HyperVertex

class TestUpdateAssociationValue(unittest.TestCase):

    def test_update_vertex_and_edge_association_value(self):
        v1 = HyperVertex("v1", 0, 0, b"1", b"1", "v1")
        v2 = HyperVertex("v2", 0, 1, b"2", b"2", "v2")
        e1 = HyperEdge("e1", 0, 0, b"3", b"3", "e1")
        e2 = HyperEdge("e2", 0, 1, b"4", b"4", "e2")

        e1.associate_vertex((v1, EnumHyperarcDirection.IN, 1.0))
        e1.associate_vertex((v2, EnumHyperarcDirection.OUT, 2.0))
        e1.associate_edge((e2, EnumHyperarcDirection.OUT, 3.0))

        # Update values
        self.assertTrue(e1.update_association_value(v1, 10.0))
        self.assertTrue(e1.update_association_value(e2, 30.0))

        # Check updated values
        for rel in e1.all_relations():
            if rel.target == v1:
                self.assertEqual(rel.value, 10.0)
            if rel.target == v2:
                self.assertEqual(rel.value, 2.0)
            if rel.target == e2:
                self.assertEqual(rel.value, 30.0)

        # Try updating a non-associated vertex
        v3 = HyperVertex("v3", 0, 2, b"5", b"5", "v3")
        self.assertFalse(e1.update_association_value(v3, 99.0))

    def test_update_multiple_and_remove(self):
        v1 = HyperVertex("v1", 0, 0, b"1", b"1", "v1")
        v2 = HyperVertex("v2", 0, 1, b"2", b"2", "v2")
        v3 = HyperVertex("v3", 0, 2, b"3", b"3", "v3")
        e1 = HyperEdge("e1", 0, 0, b"4", b"4", "e1")
        e2 = HyperEdge("e2", 0, 1, b"5", b"5", "e2")
        e3 = HyperEdge("e3", 0, 2, b"6", b"6", "e3")

        e1.associate_vertex((v1, EnumHyperarcDirection.IN, 1.0))
        e1.associate_vertex((v2, EnumHyperarcDirection.OUT, 2.0))
        e1.associate_vertex((v3, EnumHyperarcDirection.IN, 3.0))
        e1.associate_edge((e2, EnumHyperarcDirection.OUT, 4.0))
        e1.associate_edge((e3, EnumHyperarcDirection.IN, 5.0))

        # Update all values
        self.assertTrue(e1.update_association_value(v1, 10.0))
        self.assertTrue(e1.update_association_value(v2, 20.0))
        self.assertTrue(e1.update_association_value(v3, 30.0))
        self.assertTrue(e1.update_association_value(e2, 40.0))
        self.assertTrue(e1.update_association_value(e3, 50.0))

        # Check all updated
        for rel in e1.all_relations():
            if rel.target == v1:
                self.assertEqual(rel.value, 10.0)
            if rel.target == v2:
                self.assertEqual(rel.value, 20.0)
            if rel.target == v3:
                self.assertEqual(rel.value, 30.0)
            if rel.target == e2:
                self.assertEqual(rel.value, 40.0)
            if rel.target == e3:
                self.assertEqual(rel.value, 50.0)

        # Update again
        self.assertTrue(e1.update_association_value(v1, 100.0))
        for rel in e1.all_relations():
            if rel.target == v1:
                self.assertEqual(rel.value, 100.0)

        # Remove an association and try to update it
        e1.unassociate_vertex(v2)
        self.assertFalse(e1.update_association_value(v2, 999.0))
        # Ensure others are unaffected
        for rel in e1.all_relations():
            self.assertNotEqual(rel.target, v2)

if __name__ == "__main__":
    unittest.main()