import networkx as nx
from matplotlib import pyplot as plt

from himeko_hypergraph.src.elements.edge import HyperEdge
from himeko_hypergraph.src.elements.vertex import HyperVertex


def visualize_node(node: HyperVertex):
    G_viz = nx.DiGraph()
    for el in node.get_children(lambda x: True):
        if isinstance(el, HyperVertex):
            G_viz.add_node(el["name"], color="violet")
        if isinstance(el, HyperEdge):
            G_viz.add_node(el["name"], color="blue")
    nx.draw(G_viz, with_labels=True, font_weight='bold')
    plt.show()

