import pygraphviz as pgv

from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.vertex import HyperVertex


def create_dot_graph(root: HyperVertex, **kwargs):
    G = pgv.AGraph(directed=True)
    G.add_node(root.name)
    for n in root.get_children(lambda x: isinstance(x, HyperVertex)):
        G.add_node(n.name)
        # Check if we want to add stereotype
        if "stereotype" in kwargs and kwargs["stereotype"]:
            # Add connection to stereotype
            if len(n.stereotype) > 0:
                for st in n.stereotype:
                    G.add_edge(n.name, st.name, style="dashed")
    for e in root.get_children(lambda x: isinstance(x, HyperEdge)):
        G.add_node(e.name, shape="box")
        for r in e.out_relations():
            G.add_edge(e.name, r.target.name, label=str(r.value))
        for r in e.in_relations():
            G.add_edge(r.target.name, e.name,  label=str(r.value))
    # Check if composition should be visualized
    if "composition" in kwargs and kwargs["composition"]:
        if "composition_depth" in kwargs:
            G = create_composition_tree(root, G, depth=kwargs["composition_depth"])
        else:
            G = create_composition_tree(root, G)
    return G


def create_composition_tree(root: HyperVertex, G=None, depth=1):
    if G is None:
        G = pgv.AGraph(directed=True)
    # Get composition
    for n in root.get_children(lambda x: isinstance(x, HypergraphElement), depth):
        if n.parent is not None:
            G.add_edge(n.parent.name, n.name, style="dotted")
    return G


def visualize_dot_graph(G, path: str):
    G.layout(prog="dot")
    G.draw(path)
    return G


def visualize_prufer_code(code, degree, node_list, path):
    G = pgv.AGraph(directed=True)
    for i, c in enumerate(code):
        for j, n in enumerate(node_list):
            if degree[n] == 1:
                degree[n] -= 1
                degree[code[i]] -= 1
                G.add_edge(n.name, code[i].name)
                break
    G.layout(prog="dot")
    G.draw(path)
