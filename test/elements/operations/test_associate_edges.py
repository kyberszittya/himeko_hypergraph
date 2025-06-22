import unittest
from himeko.hbcm.elements.edge import HyperEdge, EnumHyperarcDirection
from himeko.hbcm.elements.vertex import HyperVertex

class TestAssociateEdges(unittest.TestCase):
    def test_associate_single_vertex(self):
        v = HyperVertex("v", 0, 0, b"1", b"1", "v")
        e = HyperEdge("e", 0, 0, b"2", b"2", "e")
        e.associate_vertex((v, EnumHyperarcDirection.IN, 1.0))
        self.assertTrue(any(rel.target == v for rel in e.all_relations()))
        self.assertEqual(e.cnt_in_relations, 1)
        self.assertEqual(e.cnt_out_relations, 0)

    def test_associate_multiple_vertices(self):
        v1 = HyperVertex("v1", 0, 0, b"1", b"1", "v1")
        v2 = HyperVertex("v2", 0, 1, b"2", b"2", "v2")
        e = HyperEdge("e", 0, 0, b"3", b"3", "e")
        e.associate_vertex((v1, EnumHyperarcDirection.IN, 1.0))
        e.associate_vertex((v2, EnumHyperarcDirection.OUT, 2.0))
        self.assertTrue(any(rel.target == v1 for rel in e.all_relations()))
        self.assertTrue(any(rel.target == v2 for rel in e.all_relations()))
        self.assertEqual(e.cnt_in_relations, 1)
        self.assertEqual(e.cnt_out_relations, 1)

    def test_associate_single_edge(self):
        e1 = HyperEdge("e1", 0, 0, b"1", b"1", "e1")
        e2 = HyperEdge("e2", 0, 1, b"2", b"2", "e2")
        e1.associate_edge((e2, EnumHyperarcDirection.OUT, 3.0))
        self.assertTrue(any(rel.target == e2 for rel in e1.all_relations()))
        self.assertEqual(e1.cnt_in_relations, 0)
        self.assertEqual(e1.cnt_out_relations, 1)

    def test_associate_vertices_and_edges(self):
        v1 = HyperVertex("v1", 0, 0, b"1", b"1", "v1")
        v2 = HyperVertex("v2", 0, 1, b"2", b"2", "v2")
        e1 = HyperEdge("e1", 0, 0, b"3", b"3", "e1")
        e2 = HyperEdge("e2", 0, 1, b"4", b"4", "e2")
        e1.associate_vertex((v1, EnumHyperarcDirection.IN, 1.0))
        e1.associate_vertex((v2, EnumHyperarcDirection.OUT, 2.0))
        e1.associate_edge((e2, EnumHyperarcDirection.OUT, 3.0))
        self.assertTrue(any(rel.target == v1 for rel in e1.all_relations()))
        self.assertTrue(any(rel.target == v2 for rel in e1.all_relations()))
        self.assertTrue(any(rel.target == e2 for rel in e1.all_relations()))
        self.assertEqual(e1.cnt_in_relations, 1)
        self.assertEqual(e1.cnt_out_relations, 2)

if __name__ == "__main__":
    unittest.main()