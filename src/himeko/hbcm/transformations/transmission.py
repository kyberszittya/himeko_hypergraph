from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.graph.prufer_sequence import generate_naive_prufer


def copy_node_list(node_list):
    """
    Copy tree
    :param tree:
    :return:
    """
    copy_node = []
    for n in node_list:
        n: HypergraphElement
        copy_node.append((n.name, n.guid, n.serial, n.timestamp, n.label, n.suid))

    # Copy tree nodes
    copy_node_map = {}
    list_copy_node = []
    # Reconstruct tree
    for t in copy_node:
        n = HyperVertex(t[0], t[3], t[2], t[1], t[5], t[4])
        list_copy_node.append(n)
        copy_node_map[t[1]] = n
    return copy_node, list_copy_node, copy_node_map


def copy_tree(root):
    code, node_list, _ = generate_naive_prufer(root)
    node_list.append(root)
    copy_node, list_copy_node, copy_node_map = copy_node_list(node_list)
    return copy_node, list_copy_node, copy_node_map, code


def transform_raw_code(root):
    copy_node, _, _, code = copy_tree(root)
    raw_code = [x.guid for x in code]
    node_code = [x[1] for x in copy_node]
    return raw_code, node_code