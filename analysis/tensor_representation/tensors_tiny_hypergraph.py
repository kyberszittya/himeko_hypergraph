import numpy as np

from hypergraphs import TinyHypergraph



def main():
    hypergraph_tensor = TinyHypergraph()
    tensor = hypergraph_tensor.tensor_star_expansion()
    tensor_clique = hypergraph_tensor.tensor_clique_expansion()
    e_dim = hypergraph_tensor.e_dim
    v_dim = hypergraph_tensor.v_dim
    tensor = hypergraph_tensor.unified_expansion()
    proj, e_diag = hypergraph_tensor.projection_unified()
    print("Tensor shape:", tensor.shape)
    print("Tensor content:\n", tensor)
    print("Projection shape:", proj.shape)
    print("Projection content:\n", proj)
    d = e_diag
    #d = e_diag
    sqrt_d = np.sqrt(d)
    inv_sqrt_d = 1.0 / sqrt_d
    diag_d = np.diag(inv_sqrt_d)
    res = np.eye(v_dim + e_dim) - (diag_d @ proj @ diag_d)
    print("Normalized adjacency matrix:")
    
    print(res)
    print(res.trace())
    eigvals, _ = np.linalg.eig(res)
    # Normalize eigenvalues
    eigvals = np.real(eigvals)
    eigvals = np.abs(eigvals) / np.sum(np.abs(eigvals))
    print("Eigenvalues:", eigvals)
    # Calculate entropy
    entropy = -np.sum(eigvals * np.log(eigvals + 1e-10))  # Adding small value to avoid log(0)
    print("Entropy:", entropy)
    print("Trace of normalized matrix:", np.trace(res))
    # Calculate determinant
    det = np.linalg.det(proj)
    print("Determinant:", det)
    # Cholesky decomposition
    try:
        L = np.linalg.cholesky(proj)
        print("Cholesky decomposition successful.")
        print("L:\n", L)
    except np.linalg.LinAlgError:
        print("Cholesky decomposition failed. Matrix may not be positive definite.")
    # SVD
    U, s, Vt = np.linalg.svd(proj)
    print("SVD U:\n", U, "\nS:\n", s, "\nVt:\n", Vt)
    # Reconstructing the matrix from SVD
    reconstructed = U @ np.diag(s) @ Vt
    print("Reconstructed matrix from SVD:\n", reconstructed)
    # Imshow of the tensor
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    plt.imshow(res, cmap=cm.Blues)
    plt.colorbar()
    plt.title("Normalized Adjacency Matrix")
    plt.show()
    

if __name__ == "__main__":
    main()
    