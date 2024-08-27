from himeko.hbcm.mapping.meta.tensor_mapping import TensorChannel, AbstractHypergraphTensorTransformation, \
    HypergraphTensor
from himeko.hbcm.mapping.tensor_mapping import StarExpansionTransformation, BijectiveCliqueExpansionTransformation


class DefaultTensorChannel(TensorChannel):

    def __init__(self, exp: AbstractHypergraphTensorTransformation):
        super().__init__(exp)
        self.__star = StarExpansionTransformation()
        self.__bijective = BijectiveCliqueExpansionTransformation()

    def receive(self, msg: HypergraphTensor):
        n_pr = len(msg.prufer_sequence)
        if msg.n == n_pr:
            return self.__star.decode(msg)
        else:
            return self.__bijective.decode(msg)
