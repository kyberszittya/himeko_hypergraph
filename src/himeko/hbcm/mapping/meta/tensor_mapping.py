import abc
from dataclasses import dataclass

from himeko.hbcm.elements.vertex import HyperVertex

import numpy as np


@dataclass
class HypergraphTensor:
    tensor: np.ndarray
    n: int
    n_e: int
    node_sequence: list
    prufer_sequence: list
    edge_order: list


class AbstractHypergraphTensorTransformation(abc.ABCMeta):

    @abc.abstractmethod
    def dimensions(self, n: HyperVertex, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def encode(self, n: HyperVertex, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, n: HypergraphTensor, **kwargs):
        raise NotImplementedError


class TensorChannel(object):

    def __init__(self, exp: AbstractHypergraphTensorTransformation):
        self._expansion = exp

    def transmit(self, root: HyperVertex):
        tensor, n, e = self._expansion.encode(root)
        return tensor, n, e, root.prufer_code, root.permutation_sequence

    @abc.abstractmethod
    def receive(self, msg: HypergraphTensor):
        raise NotImplementedError
