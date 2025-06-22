import unittest
from himeko.hbcm.elements.edge import HyperEdge, EnumHyperarcDirection
from himeko.hbcm.elements.vertex import HyperVertex

class TestRemoveEdges(unittest.TestCase):
    def test_unassociate_vertex_and_edge(self):
        v1 = HyperVertex("v1", 0, 0, b"1", b"1", "v1")
        v2 = HyperVertex("v2", 0, 1, b"2", b"2", "v2")
        e1 = HyperEdge("e1", 0, 0, b"3", b"3", "e1")
        e2 = HyperEdge("e2", 0, 1, b"4", b"4", "e2")

        e1.associate_vertex((v1, EnumHyperarcDirection.IN, 1.0))
        e1.associate_edge((e2, EnumHyperarcDirection.OUT, 2.0))

        self.assertTrue(any(rel.target == v1 for rel in e1.all_relations()))
        self.assertTrue(any(rel.target == e2 for rel in e1.all_relations()))

        e1.unassociate_vertex(v1)
        e1.unassociate_edge(e2)

        self.assertFalse(any(rel.target == v1 for rel in e1.all_relations()))
        self.assertFalse(any(rel.target == e2 for rel in e1.all_relations()))

        self.assertEqual(e1.cnt_in_relations, 0)
        self.assertEqual(e1.cnt_out_relations, 0)

    def test_multiple_additions_and_removals(self):
        # Create vertices and edges
        vertices = [HyperVertex(f"v{i}", 0, i, bytes([i]), bytes([i]), f"v{i}") for i in range(5)]
        edges = [HyperEdge(f"e{i}", 0, i, bytes([10+i]), bytes([10+i]), f"e{i}") for i in range(3)]
        main_edge = HyperEdge("main", 0, 99, b"m", b"m", "main")

        # Add all vertices as IN, all edges as OUT
        for v in vertices:
            main_edge.associate_vertex((v, EnumHyperarcDirection.IN, 1.0))
        for e in edges:
            main_edge.associate_edge((e, EnumHyperarcDirection.OUT, 2.0))

        # Check all associations exist
        for v in vertices:
            self.assertTrue(any(rel.target == v for rel in main_edge.all_relations()))
        for e in edges:
            self.assertTrue(any(rel.target == e for rel in main_edge.all_relations()))

        self.assertEqual(main_edge.cnt_in_relations, len(vertices))
        self.assertEqual(main_edge.cnt_out_relations, len(edges))

        # Remove all vertices and edges
        for v in vertices:
            main_edge.unassociate_vertex(v)
        for e in edges:
            main_edge.unassociate_edge(e)

        # Check all associations are removed
        for v in vertices:
            self.assertFalse(any(rel.target == v for rel in main_edge.all_relations()))
        for e in edges:
            self.assertFalse(any(rel.target == e for rel in main_edge.all_relations()))

        self.assertEqual(main_edge.cnt_in_relations, 0)
        self.assertEqual(main_edge.cnt_out_relations, 0)

    def test_remove_single_edge_among_multiple(self):
        # Create vertices and edges
        v1 = HyperVertex("v1", 0, 0, b"1", b"1", "v1")
        v2 = HyperVertex("v2", 0, 1, b"2", b"2", "v2")
        e1 = HyperEdge("e1", 0, 0, b"3", b"3", "e1")
        e2 = HyperEdge("e2", 0, 1, b"4", b"4", "e2")
        e3 = HyperEdge("e3", 0, 2, b"5", b"5", "e3")

        # Associate two vertices and two edges to e1
        e1.associate_vertex((v1, EnumHyperarcDirection.IN, 1.0))
        e1.associate_vertex((v2, EnumHyperarcDirection.IN, 1.0))
        e1.associate_edge((e2, EnumHyperarcDirection.OUT, 2.0))
        e1.associate_edge((e3, EnumHyperarcDirection.OUT, 2.0))

        # Remove only e2
        e1.unassociate_edge(e2)

        # e2 should be removed, e3 should remain
        self.assertFalse(any(rel.target == e2 for rel in e1.all_relations()))
        self.assertTrue(any(rel.target == e3 for rel in e1.all_relations()))
        # Both vertices should remain
        self.assertTrue(any(rel.target == v1 for rel in e1.all_relations()))
        self.assertTrue(any(rel.target == v2 for rel in e1.all_relations()))

        # Counters should reflect the removals
        self.assertEqual(e1.cnt_in_relations, 2)
        self.assertEqual(e1.cnt_out_relations, 1)

    def test_remove_single_vertex_among_multiple(self):
        # Create vertices and edges
        v1 = HyperVertex("v1", 0, 0, b"1", b"1", "v1")
        v2 = HyperVertex("v2", 0, 1, b"2", b"2", "v2")
        e1 = HyperEdge("e1", 0, 0, b"3", b"3", "e1")
        e2 = HyperEdge("e2", 0, 1, b"4", b"4", "e2")
        e3 = HyperEdge("e3", 0, 2, b"5", b"5", "e3")

        # Associate two vertices and two edges to e1
        e1.associate_vertex((v1, EnumHyperarcDirection.IN, 1.0))
        e1.associate_vertex((v2, EnumHyperarcDirection.IN, 1.0))
        e1.associate_edge((e2, EnumHyperarcDirection.OUT, 2.0))
        e1.associate_edge((e3, EnumHyperarcDirection.OUT, 2.0))

        # Remove only v1
        e1.unassociate_vertex(v1)

        # v1 should be removed, v2 should remain
        self.assertFalse(any(rel.target == v1 for rel in e1.all_relations()))
        self.assertTrue(any(rel.target == v2 for rel in e1.all_relations()))
        # Both edges should remain
        self.assertTrue(any(rel.target == e2 for rel in e1.all_relations()))
        self.assertTrue(any(rel.target == e3 for rel in e1.all_relations()))

        # Counters should reflect the removals
        self.assertEqual(e1.cnt_in_relations, 1)
        self.assertEqual(e1.cnt_out_relations, 2)

    def test_complex_multiple_add_remove(self):
        # Create vertices and edges
        vertices = [HyperVertex(f"v{i}", 0, i, bytes([i]), bytes([i]), f"v{i}") for i in range(4)]
        edges = [HyperEdge(f"e{i}", 0, i, bytes([10+i]), bytes([10+i]), f"e{i}") for i in range(4)]
        main_edge = HyperEdge("main", 0, 99, b"m", b"m", "main")

        # Associate all vertices as IN, all edges as OUT
        for v in vertices:
            main_edge.associate_vertex((v, EnumHyperarcDirection.IN, 1.0))
        for e in edges:
            main_edge.associate_edge((e, EnumHyperarcDirection.OUT, 2.0))

        # Remove some vertices and edges
        main_edge.unassociate_vertex(vertices[1])
        main_edge.unassociate_vertex(vertices[3])
        main_edge.unassociate_edge(edges[0])
        main_edge.unassociate_edge(edges[2])

        # Check removed associations
        self.assertFalse(any(rel.target == vertices[1] for rel in main_edge.all_relations()))
        self.assertFalse(any(rel.target == vertices[3] for rel in main_edge.all_relations()))
        self.assertFalse(any(rel.target == edges[0] for rel in main_edge.all_relations()))
        self.assertFalse(any(rel.target == edges[2] for rel in main_edge.all_relations()))

        # Check remaining associations
        self.assertTrue(any(rel.target == vertices[0] for rel in main_edge.all_relations()))
        self.assertTrue(any(rel.target == vertices[2] for rel in main_edge.all_relations()))
        self.assertTrue(any(rel.target == edges[1] for rel in main_edge.all_relations()))
        self.assertTrue(any(rel.target == edges[3] for rel in main_edge.all_relations()))

        # Check counters
        self.assertEqual(main_edge.cnt_in_relations, 2)
        self.assertEqual(main_edge.cnt_out_relations, 2)

        # Remove all remaining
        main_edge.unassociate_vertex(vertices[0])
        main_edge.unassociate_vertex(vertices[2])
        main_edge.unassociate_edge(edges[1])
        main_edge.unassociate_edge(edges[3])

        # All associations should be gone
        self.assertEqual(main_edge.cnt_in_relations, 0)
        self.assertEqual(main_edge.cnt_out_relations, 0)
        self.assertFalse(any(True for _ in main_edge.all_relations()))

if __name__ == "__main__":
    unittest.main()