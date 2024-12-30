from random import random

from himeko.common.clock import AbstractClock
from himeko.hbcm.elements.edge import EnumHyperarcDirection
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElementsClock


class SingleFixedHypergraphGenerator7Nodes():

    def __init__(self, clock: AbstractClock) -> None:
        super().__init__()
        self._clock = clock
        self._factory = FactoryHypergraphElementsClock(self._clock)

    def generate(self):
        root = self._factory.create_vertex("root")
        # Create vertices for root
        _vertices = []
        for i in range(7):
            v = self._factory.create_vertex("v{}".format(i), root)
            _vertices.append(v)
        # Create hyperedges
        _edges = []
        for i in range(4):
            e = self._factory.create_edge("e{}".format(i), root)
            _edges.append(e)
        dir = EnumHyperarcDirection.UNDEFINED
        # Associate vertices in a fixed order
        # Edge 1
        _edges[0].associate_vertex((_vertices[0], dir, random()))
        _edges[0].associate_vertex((_vertices[1], dir, random()))
        _edges[0].associate_vertex((_vertices[2], dir, random()))
        _edges[0].associate_vertex((_vertices[3], dir, random()))
        # Edge 2
        _edges[1].associate_vertex((_vertices[3], dir, random()))
        _edges[1].associate_vertex((_vertices[4], dir, random()))
        _edges[1].associate_vertex((_vertices[5], dir, random()))
        # Edge 3
        _edges[2].associate_vertex((_vertices[4], dir, random()))
        _edges[2].associate_vertex((_vertices[6], dir, random()))
        # Edge 4
        _edges[3].associate_vertex((_vertices[2], dir, random()))
        _edges[3].associate_vertex((_vertices[5], dir, random()))
        _edges[3].associate_vertex((_vertices[6], dir, random()))
        return root
