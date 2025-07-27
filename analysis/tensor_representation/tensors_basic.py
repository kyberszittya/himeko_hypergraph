import numpy as np

"""
Used hypergraph

vertices: 0, 1, 2, 3
edges: ((0, 1, 3), (1, 2), (2, 3), (0, 2, 3))

"""

v_dim = 4
e_dim = 4

def small_hypergraph_tensor_clique_expansion():
    tensor_e_1 = np.zeros((e_dim, v_dim, v_dim))
    tensor_e_1[0, :, :] = np.array([
        [0, 1, 0, 1],
        [1, 0, 0, 1],
        [0, 0, 0, 0],
        [1, 1, 0, 0]
    ])
    tensor_e_1[1, :, :] = np.array([
        [0, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 0]        
    ])
    tensor_e_1[2, :, :] = np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ])
    tensor_e_1[3, :, :] = np.array([
        [0, 0, 1, 1],
        [0, 0, 0, 0],
        [1, 0, 0, 1],
        [1, 0, 1, 0]
        
    ])
    return tensor_e_1


def small_hypergraph_tensor_star_expansion():
    tensor_e_1 = np.zeros((e_dim, v_dim + e_dim, v_dim + e_dim))
    tensor_e_1[0, :, :] = np.array([
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ])
    tensor_e_1[1, :, :] = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ])
    tensor_e_1[2, :, :] = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ])
    tensor_e_1[3, :, :] = np.array([
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 0, 0, 0, 0]
    ])
    return tensor_e_1

def main():
    tensor = small_hypergraph_tensor_star_expansion()
    tensor_clique = small_hypergraph_tensor_clique_expansion()
    #tensor[:, :v_dim, :v_dim] = tensor_clique[:, :v_dim, :v_dim]
    proj = np.einsum("ijk->jk", tensor)
    e_diag = np.array([0, 0, 0, 0, 3, 2, 2, 3])
    v_diag = np.array([3, 2, 2, 3, 0, 0, 0, 0])
    proj = proj + np.eye(v_dim + e_dim)
    print("Tensor shape:", tensor.shape)
    print("Tensor content:\n", tensor)
    print("Projection shape:", proj.shape)
    print("Projection content:\n", proj)
    d = e_diag + v_diag
    #d = e_diag
    sqrt_d = np.sqrt(d)
    inv_sqrt_d = 1.0 / sqrt_d
    diag_d = np.diag(inv_sqrt_d)
    res = diag_d @ -proj @ diag_d
    
    print(res)
    print(res.trace())
    print(np.linalg.eig(res))
    # Imshow of the tensor
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    plt.imshow(res, cmap=cm.Blues)
    plt.show()


if __name__ == "__main__":
    main()