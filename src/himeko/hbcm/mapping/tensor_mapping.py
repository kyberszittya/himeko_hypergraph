from himeko.hbcm.elements.edge import HyperEdge, EnumRelationDirection
from himeko.hbcm.elements.vertex import HyperVertex

import numpy as np

from himeko.hbcm.mapping.meta.tensor_mapping import AbstractHypergraphTensorTransformation, HypergraphTensor


class BijectiveCliqueExpansionTransformation(metaclass=AbstractHypergraphTensorTransformation):

    def __init__(self):
        super().__init__()

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
                e.associate_vertex((msg.node_sequence[y], EnumRelationDirection.OUT, v))
                e.associate_vertex((msg.node_sequence[x], EnumRelationDirection.IN, v))




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
            for x in e.permutation_tuples():
                # Add edge outgoing from util node
                i = perm[x[0]]
                e_j = perm[e]
                adj[i, e_j] = float(x[2])
                # Outgoing edge
                j = perm[x[1]]
                adj[e_j, j] = float(x[2])
            e.adjacency_tensor = adj
            tensor[ei] = adj
        return tensor, n, n_e

    def decode(self, n:  HypergraphTensor):
        # Decode hypergraph from tensor
        # Check if clique or star expansion is used (based on the dimension of the tensor)
        for i, e in enumerate(n.edge_order):
            e: HyperEdge
            print(np.nonzero(n.tensor[i]))
