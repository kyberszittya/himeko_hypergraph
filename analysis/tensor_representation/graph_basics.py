import numpy as np

class SimpleGraph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v):
        if u not in self.adj:
            self.adj[u] = set()
        if v not in self.adj:
            self.adj[v] = set()
        self.adj[u].add(v)
        self.adj[v].add(u)  # For undirected graph

    def neighbors(self, node):
        return self.adj.get(node, set())

    def nodes(self):
        return list(self.adj.keys())

    def adjacency_matrix(self):
        nodes = sorted(self.adj.keys())
        idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)
        matrix = np.zeros((n, n), dtype=int)
        for u in nodes:
            for v in self.adj[u]:
                matrix[idx[u], idx[v]] = 1
        return matrix, nodes  # nodes gives the order

    def __repr__(self):
        return f"SimpleGraph({self.adj})"


# Example usage:
if __name__ == "__main__":
    g = SimpleGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    print(g)
    matrix, nodes = g.adjacency_matrix()
    print("Nodes order:", nodes)
    print("Adjacency matrix:")
    for row in matrix:
        print(row)
    d = np.array([2, 2, 2])  # Example degree array
    sqrt_d = np.sqrt(d)
    inv_sqrt_d = 1.0 / sqrt_d
    diag_d = np.diag(inv_sqrt_d)
    res = diag_d @ matrix @ diag_d
    print("Normalized adjacency matrix:")
    print(res)
    res = np.eye(len(nodes)) - res
    print("Trace of normalized matrix:", np.trace(res))
    # Get eigenvalues
    eigenvalues, _ = np.linalg.eig(res)
    print("Eigenvalues:", eigenvalues)