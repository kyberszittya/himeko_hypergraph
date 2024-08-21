import abc

from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex

import numpy as np


class AbstractHypergraphTensorTransformation(abc.ABCMeta):

    @abc.abstractmethod
    def dimensions(self, n: HyperVertex, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def encode(self, n: HyperVertex, **kwargs):
        raise NotImplementedError


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
                i = perm[x[0]]
                j = perm[e]
                adj[i, j] = float(x[2])
            e.adjacency_tensor = adj
            tensor[ei] = adj
        return tensor, n, n_e
