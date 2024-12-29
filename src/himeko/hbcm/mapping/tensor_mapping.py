from himeko.hbcm.elements.edge import HyperEdge, EnumHyperarcDirection, HyperArc
from himeko.hbcm.elements.vertex import HyperVertex

import numpy as np

from himeko.hbcm.mapping.meta.tensor_mapping import AbstractHypergraphTensorTransformation, HypergraphTensor


class BijectiveCliqueExpansionTransformation(metaclass=AbstractHypergraphTensorTransformation):

    def __init__(self, **kwargs):
        super().__init__()
        # Check if aggregate function is provided
        if "aggregate_function" in kwargs:
            self.aggregate_function = kwargs["aggregate_function"]
        else:
            self.aggregate_function = lambda x, y: (float(x) + float(y)) / 2

    def dimensions(self, root: HyperVertex, **kwargs):
        return len(list(root.children_permutation_sequence_nodes)), len(list(root.edge_order))

    def encode(self, root: HyperVertex, **kwargs):
        perm = root.element_permutation
        n, n_e = self.dimensions(root)
        edges = root.edge_order
        tensor = np.zeros((n_e, n, n))
        # Iterate over all edges
        for ei, e in enumerate(edges):
            e: HyperEdge
            adj = np.zeros((n, n))
            for x in e.permutation_tuples():
                i = perm[x[0]]
                j = perm[x[1]]
                if x[4] == EnumHyperarcDirection.UNDEFINED and x[5] == EnumHyperarcDirection.UNDEFINED:
                    adj[i, j] = self.aggregate_function(x[3], x[2])
                else:
                    adj[i, j] = float(x[2])
            e.adjacency_tensor = adj
            tensor[ei] = adj
        return tensor, n, n_e

    def decode(self, msg: HypergraphTensor):
        # Clique expansion
        for i, e in enumerate(msg.edge_order):
            e: HyperEdge
            edge_sets = set()
            nonzeros = np.argwhere(msg.tensor[i])
            for x,y in nonzeros:
                edge_sets.add((x, y, msg.tensor[i, x, y]))
            for x, y, v in edge_sets:
                e.associate_vertex((msg.node_sequence[y], EnumHyperarcDirection.OUT, v))
                e.associate_vertex((msg.node_sequence[x], EnumHyperarcDirection.IN, v))


class StarExpansionTransformation(metaclass=AbstractHypergraphTensorTransformation):

    def __init__(self):
        super().__init__()

    def dimensions(self, root: HyperVertex, **kwargs):
        return len(list(root.children_permutation_sequence)), len(list(root.edge_order))

    def encode(self, root: HyperVertex, **kwargs):
        perm = root.element_permutation
        n, n_e = self.dimensions(root)
        edges = root.edge_order
        tensor = np.zeros((n_e, n, n))
        # Iterate over all edges
        for ei, e in enumerate(edges):
            e: HyperEdge
            adj = np.zeros((n, n))
            e_j = perm[e]
            # Iterate over outgoing relations
            for a in e.out_relations():
                a: HyperArc
                i = perm[a.target]
                adj[e_j, i] = float(a.value)
            # Iterate over incoming relations
            for a in e.in_relations():
                a: HyperArc
                i = perm[a.target]
                adj[i, e_j] = float(a.value)
            e.adjacency_tensor = adj
            tensor[ei] = adj
        return tensor, n, n_e

    def decode(self, msg:  HypergraphTensor):
        # Decode hypergraph from tensor
        # Check if clique or star expansion is used (based on the dimension of the tensor)
        for i, e in enumerate(msg.edge_order):
            e: HyperEdge
            index_edge = msg.node_sequence.index(e)
            edge_sets = set()
            nonzeros = np.argwhere(msg.tensor[i])
            for x, y in nonzeros:
                edge_sets.add((i, x, y, msg.tensor[i, x, y]))
            for _, x, y, v in edge_sets:
                if x == index_edge:
                    e.associate_vertex((msg.node_sequence[y], EnumHyperarcDirection.OUT, v))
                elif y == index_edge:
                    e.associate_vertex((msg.node_sequence[x], EnumHyperarcDirection.IN, v))

