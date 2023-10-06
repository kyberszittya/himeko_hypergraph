import networkx as nx
from matplotlib import pyplot as plt

from himeko_hypergraph.src.elements.edge import HyperEdge
from himeko_hypergraph.src.elements.vertex import HyperVertex


def visualize_node(node: HyperVertex, viz_parent=False):
    G_viz = nx.DiGraph()
    color_map = []
    for el in node.get_children(lambda x: True):
        if isinstance(el, HyperVertex):
            G_viz.add_node(el["name"], color="purple")
            color_map.append("purple")
        if isinstance(el, HyperEdge):
            G_viz.add_node(el["name"], color="blue")
            color_map.append("blue")
            for re in el.in_relations():
                G_viz.add_edge(re.target["name"], el["name"])
            for re in el.out_relations():
                G_viz.add_edge(el["name"], re.target["name"])
        if viz_parent:
            G_viz.add_edge(node["name"], el["name"])
    nx.draw(G_viz, with_labels=True, node_color=color_map)
    plt.show()

