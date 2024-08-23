from himeko.hbcm.elements.vertex import HyperVertex


class ExecutableHyperVertex(HyperVertex):

    def __call__(self, *args, **kwargs):
        return self.operate(*args, **kwargs)

    def operate(self, *args, **kwargs):
        raise NotImplementedError