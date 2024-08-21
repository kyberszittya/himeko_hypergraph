from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex

import numpy as np


def tensor_mapping(root: HyperVertex, **kwargs):
    perm = root.element_permutation
    seq = list(root.children_permutation_sequence_nodes)
    n = len(seq)
    edges = root.edge_order
    n_e = len(edges)
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

