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
    code = []
    nodes = []
    while len(fringe) != 0:
        node = fringe.pop()
        u = node.parent
        if u is not None:
            nodes.append(node)
            code.append(u)
            if u not in degree_map:
                degree_map[u] = u.count_composite_elements + 1
            degree_map[u] -= 1
            if degree_map[u] == 1:
                fringe.append(u)
    return nodes, code
