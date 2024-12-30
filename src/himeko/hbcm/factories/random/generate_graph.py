import abc
import random

from himeko.common.clock import AbstractClock
from himeko.hbcm.elements.edge import HyperEdge, EnumHyperarcDirection
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElementsClock


class RandomHypergraphGenerator(abc.ABC):

    def __init__(self, clock: AbstractClock) -> None:
        super().__init__()
        self._clock = clock
        self._factory = FactoryHypergraphElementsClock(self._clock)

    @abc.abstractmethod
    def generate(self, n: int, e: int, **kwargs):
        raise NotImplementedError



class RandomFullHypergraphGenerator(RandomHypergraphGenerator):

    def __init__(self, clock: AbstractClock) -> None:
        super().__init__(clock)

    def generate(self, n: int, e: int, **kwargs):
        root = self._factory.create_vertex("root")
        # Create vertices for root
        vertices = []
        for i in range(n):
            v = self._factory.create_vertex("v{}".format(i), root)
            vertices.append(v)
        # Create hyperedges
        for i in range(e):
            self._factory.create_edge("e{}".format(i), root)
        # Create dense hyperarcs (associate each node with each edge)
        for e in root.get_all_children(lambda x: isinstance(x, HyperEdge)):
            e: HyperEdge
            for v in vertices:
                # Get random direction (random between 0,1,2)
                match random.randint(0, 2):
                    case 0:
                        dir = EnumHyperarcDirection.IN
                    case 1:
                        dir = EnumHyperarcDirection.OUT
                    case 2:
                        dir = EnumHyperarcDirection.UNDEFINED
                dir = EnumHyperarcDirection.UNDEFINED
                # Get random value
                val = random.random()
                # Associate each vertex with the edge
                e.associate_vertex((v, dir, val))

        return root


class RandomFullHypergraphGeneratorDirected(RandomHypergraphGenerator):

    def __init__(self, clock: AbstractClock) -> None:
        super().__init__(clock)

    def generate(self, n: int, e: int, **kwargs):
        root = self._factory.create_vertex("root")
        # Create vertices for root
        vertices = []
        for i in range(n):
            v = self._factory.create_vertex("v{}".format(i), root)
            vertices.append(v)
        # Create hyperedges
        for i in range(e):
            self._factory.create_edge("e{}".format(i), root)
        # Create dense hyperarcs (associate each node with each edge)
        for e in root.get_all_children(lambda x: isinstance(x, HyperEdge)):
            e: HyperEdge
            for v in vertices:
                # Get random direction (random between 0,1,2)
                dir = EnumHyperarcDirection.UNDEFINED
                match random.randint(0, 2):
                    case 0:
                        dir = EnumHyperarcDirection.IN
                    case 1:
                        dir = EnumHyperarcDirection.OUT
                    case 2:
                        dir = EnumHyperarcDirection.UNDEFINED
                # Get random value
                val = random.random()
                # Associate each vertex with the edge
                e.associate_vertex((v, dir, val))

        return root
