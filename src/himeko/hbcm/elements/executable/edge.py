from himeko.hbcm.elements.edge import HyperEdge


class ExecutableHyperEdge(HyperEdge):

    def __call__(self, *args, **kwargs):
        return self.operate(*args, **kwargs)

    def operate(self, *args, **kwargs):
        raise NotImplementedError

    async def async_operate(self, *args, **kwargs):
        return await self.operate(*args, *kwargs)