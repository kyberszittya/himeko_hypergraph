import numpy as np
import abc
"""
Used hypergraph

vertices: 0, 1, 2, 3
edges: ((0, 1, 3), (1, 2), (2, 3), (0, 2, 3))

"""

class HypergraphTensor(abc.ABC):
    @abc.abstractmethod
    def tensor_clique_expansion(self):
        pass

    @abc.abstractmethod
    def tensor_star_expansion(self):
        pass

    def unified_expansion(self):
        _e_dim = self.e_dim
        _v_dim = self.v_dim
        # Unified expansion tensor
        tensor_star = self.tensor_star_expansion()
        tensor_clique = self.tensor_clique_expansion()
        tensor_e_1 = np.zeros((_e_dim, _v_dim + _e_dim, _v_dim + _e_dim))
        tensor_e_1[:, :, :] = tensor_star
        tensor_e_1[:, :_v_dim, :_v_dim] = tensor_clique
        # Degree matrices
        return tensor_e_1

    def projection_unified(self):
        tensor = self.unified_expansion()
        proj = np.einsum("ijk->jk", tensor)
        e_diag = np.sum(proj, axis=1)
        return proj, e_diag
    
    def projection_clique(self):
        tensor = self.tensor_clique_expansion()
        proj = np.einsum("ijk->jk", tensor)
        e_diag = np.sum(proj, axis=1)
        return proj, e_diag
    
    def projection_star(self):
        tensor = self.tensor_star_expansion()
        proj = np.einsum("ijk->jk", tensor)
        e_diag = np.sum(proj, axis=1)
        return proj, e_diag


class SmallHypergraphTensor(HypergraphTensor):
    __v_dim = 4
    __e_dim = 4

    def tensor_clique_expansion(self):
        _e_dim = self.e_dim
        _v_dim = self.v_dim
        # Clique expansion tensor
        tensor_e_1 = np.zeros((_e_dim, _v_dim, _v_dim))
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


    def tensor_star_expansion(self):
        _e_dim = self.e_dim
        _v_dim = self.v_dim
        # Star expansion tensor
        tensor_e_1 = np.zeros((_e_dim, _v_dim + _e_dim, _v_dim + _e_dim))
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
    
    
    @property
    def v_dim(self):
        return SmallHypergraphTensor.__v_dim
    
    @property
    def e_dim(self):
        return SmallHypergraphTensor.__e_dim


class TinyHypergraph(HypergraphTensor):
    __v_dim = 3
    __e_dim = 2

    def tensor_clique_expansion(self):
        _e_dim = self.e_dim
        _v_dim = self.v_dim
        # Clique expansion tensor
        tensor_e_1 = np.zeros((_e_dim, _v_dim, _v_dim))
        tensor_e_1[0, :, :] = np.array([
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0]
        ])
        tensor_e_1[1, :, :] = np.array([
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ])
        return tensor_e_1

    def tensor_star_expansion(self):
        _e_dim = self.e_dim
        _v_dim = self.v_dim
        # Star expansion tensor
        tensor_e_1 = np.zeros((_e_dim, _v_dim + _e_dim, _v_dim + _e_dim))
        tensor_e_1[0, :, :] = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0]
        ])
        tensor_e_1[1, :, :] = np.array([
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0]
        ])
        return tensor_e_1
    
    @property
    def v_dim(self):
        return TinyHypergraph.__v_dim
    
    @property
    def e_dim(self):
        return TinyHypergraph.__e_dim
    
class SmallHypergraph2(HypergraphTensor):
    __v_dim = 4
    __e_dim = 2

    def tensor_clique_expansion(self):
        _e_dim = self.e_dim
        _v_dim = self.v_dim
        # Clique expansion tensor
        tensor_e_1 = np.zeros((_e_dim, _v_dim, _v_dim))
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


    def tensor_star_expansion(self):
        _e_dim = self.e_dim
        _v_dim = self.v_dim
        # Star expansion tensor
        tensor_e_1 = np.zeros((_e_dim, _v_dim + _e_dim, _v_dim + _e_dim))
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
    
    
    @property
    def v_dim(self):
        return SmallHypergraphTensor.__v_dim
    
    @property
    def e_dim(self):
        return SmallHypergraphTensor.__e_dim
