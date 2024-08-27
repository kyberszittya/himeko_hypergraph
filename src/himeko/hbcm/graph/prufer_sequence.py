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


def create_node_map(root):
    degree_map = {}
    node_map = {}
    for n in root.get_all_children(lambda x: True):
        degree_map[n.guid] = n.count_composite_elements + 1
        node_map[n.guid] = n
    return degree_map, node_map


def generate_naive_prufer(root):
    # As in S. Caminitri et al. 2007
    degree_map, node_map = create_node_map(root)
    degree_map[root.guid] = root.count_composite_elements + 1
    node_map[root.guid] = root
    nodes = degree_map.keys()
    node_list = []
    code = []
    # Nodes
    for n in nodes:
        if degree_map[n] == 1:
            u = node_map[n].parent
            if u is None:
                continue
            # Decrease degree of parent in the map
            degree_map[u.guid] -= 1
            # Append GUID to code
            code.append(u)
            node_list.append(node_map[n])
            while degree_map[u.guid] == 1 and u.guid < n:
                # Add parent to fringe
                p = u
                u = u.parent
                if u is None:
                    break
                degree_map[u.guid] -= 1
                if u.guid not in degree_map:
                    break
                code.append(u)
                node_list.append(node_map[p.guid])
    return code, node_list, node_map


def reconstruct_naive_prufer(code, node_guids: typing.List[bytes], node_dict: typing.Dict):
    """
    Reconstruct tree from Prüfer-like code
    :param code: Prüfer sequence
    :param node_guids: Nodes (GUIDS)
    :param node_dict: Node-element dictionary
    :return:
    """
    # Create permutation
    degree = {}
    for x in node_guids:
        degree[x] = 1
    for x in code:
        degree[x] += 1
    for i, c in enumerate(code):
        for j, n in enumerate(node_guids):
            if degree[n] == 1:
                degree[n] -= 1
                degree[c] -= 1
                node_dict[c].add_element(
                    node_dict[n]
                )
                break
    # Get root
    res = node_dict[node_guids[-1]]
    n = len(code) + 2
    for _ in range(n):
        if res.parent is None:
            return res
        res = res.parent

