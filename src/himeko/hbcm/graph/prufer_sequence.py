import typing
from collections import deque


def micikievus_code(root):
    # Collect leaves
    leafs = list(root.get_leaf_elements())
    # Init queue and degree map
    fringe = deque()
    degree_map = {}
    for leaf in leafs:
        fringe.appendleft(leaf)
        degree_map[leaf] = 1
    # Deo & Micikevicius sequence
    while len(fringe) != 0:
        node = fringe.pop()
        u = node.parent
        if u is not None:
            # Node (deleted leaf), code
            yield node, u
            if u not in degree_map:
                degree_map[u] = u.count_composite_elements + 1
            degree_map[u] -= 1
            if degree_map[u] == 1:
                fringe.appendleft(u)


def create_permutation_map(code, root):
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


def create_permutation_sequence(code, permutation):
    """
    Create permutation from Prüfer-like code for proper indexing
    :param code:
    :return:
    """
    # Create permutation
    for i, (node, _) in enumerate(code):
        yield permutation[node]



def reconstruct_naive_prufer(code, node_guids, node_dict: typing.Dict):
    """
    Reconstruct tree from Prüfer-like code
    :param code: Prüfer sequence
    :param node_guids: Nodes (GUIDS)
    :return:
    """
    # Create permutation
    n = len(code) + 2
    print(node_guids)
    degree = {}
    for x in node_guids:
        degree[x] = 1
    for x in code:
        degree[x] += 1
    for i in range(len(code)):
        for j in range(n):
            if degree[j] == 1:
                degree[j] -= 1
                degree[code[i]] -= 1
                #node_dict[j].add_child(node_dict[code[i]])
                break
