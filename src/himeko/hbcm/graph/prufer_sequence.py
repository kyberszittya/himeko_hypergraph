from collections import deque


def micikievus_code(root):
    # Collect leaves
    leafs = list(root.get_leaf_elements())
    # Init queue and degree map
    fringe = deque()
    degree_map = {}
    for leaf in leafs:
        fringe.append(leaf)
        degree_map[leaf] = 1
    # Deo & Micikevicius sequence
    while len(fringe) != 0:
        node = fringe.popleft()
        u = node.parent
        if u is not None:
            # Node (deleted leaf), code
            yield node, u
            if u not in degree_map:
                degree_map[u] = u.count_composite_elements + 1
            degree_map[u] -= 1
            if degree_map[u] == 1:
                fringe.append(u)


def create_permutation(code, root):
    """
    Create permutation from Prüfer-like code for proper indexing
    :param code:
    :return:
    """
    # Create permutation
    perm = {}
    perm_reverse = {}
    for i, (node, _) in enumerate(code + [(root, None)]):
        perm[node] = i
        perm_reverse[i] = node
    return perm, perm_reverse
