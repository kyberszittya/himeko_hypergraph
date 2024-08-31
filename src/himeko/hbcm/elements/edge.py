import hashlib
import typing
from dataclasses import dataclass
from enum import Enum

from himeko.hbcm.elements.element import HypergraphElement, HypergraphMetaElement
from himeko.hbcm.elements.interfaces.base_interfaces import IComposable
from himeko.hbcm.elements.interfaces.transformation_interfaces import ITensorTransformation

from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.exceptions.basic_exceptions import InvalidHypergraphElementException, \
    InvalidRelationDirection


class EnumRelationDirection(Enum):
    UNDEFINED = 0
    IN = 1
    OUT = 2
    TEMPLATE = -1

    def __str__(self):
        match(self):
            case EnumRelationDirection.UNDEFINED:
                return "--"
            case EnumRelationDirection.IN:
                return "<-"
            case EnumRelationDirection.OUT:
                return "->"
            case _:
                raise InvalidRelationDirection("Invalid direction is provided during relation creation")


@dataclass
class ReferenceQuery(object):
    reference_query: str


class HypergraphRelation(HypergraphMetaElement):

    def __init__(self, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, value,
                 parent: HypergraphElement, target: HypergraphElement, direction: EnumRelationDirection):
        super().__init__(timestamp, serial, guid, suid, label, parent)
        self.__value = value
        self.__target = target
        self.__dir = direction


    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, v):
        self.__value = v

    @property
    def direction(self):
        return self.__dir

    @direction.setter
    def direction(self, direction: EnumRelationDirection):
        self.__dir = direction

    @property
    def target(self):
        return self.__target

    def is_out(self):
        return self.__dir == EnumRelationDirection.UNDEFINED or self.__dir == EnumRelationDirection.OUT

    def is_in(self):
        return self.__dir == EnumRelationDirection.UNDEFINED or self.__dir == EnumRelationDirection.IN

    # Overload functions
    def __iadd__(self, other):
        self.__value += other

    def __isub__(self, other):
        self.__value -= other

    def __itruediv__(self, other):
        self.__value /= other

    def __imul__(self, other):
        self.__value *= other



def relation_label_default(e0: HypergraphElement, v0: HyperVertex, r: EnumRelationDirection):
    return f"{e0.label}{str(r)}{v0.label}"


def relation_name_default(e0: HypergraphElement, v0: HyperVertex, r: EnumRelationDirection):
    return f"{e0.name}{str(r)}{v0.label}"


class HyperEdge(HypergraphElement, ITensorTransformation, IComposable):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphElement]=None) -> None:
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        # Parent
        if parent is not None:
            parent: HyperVertex
            parent.add_element(self)
        # Relations
        self.__relations: typing.Dict[bytes, HypergraphRelation] = {}
        # Vertex associations
        self.__associations: typing.Dict[bytes, HypergraphRelation] = {}
        # Counts
        self.__cnt_in_relations = 0
        self.__cnt_out_relations = 0
        # Permutation tuples
        self._permutation_tuples = []
        # Adjacency tensor
        self._adj = None

    def __create_default_relation_guid(self, label: str) -> bytes:
        return hashlib.sha384(label.encode('utf-8')).digest()

    def associate_vertex(self, r: typing.Tuple[HyperVertex, EnumRelationDirection, float|typing.Iterable]):
        v, d, _val = r
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to add incompatible element to graph")
        __lbl = relation_label_default(self, v, d)
        guid = self.__create_default_relation_guid(__lbl)
        # TODO: SUID revamp
        suid = guid
        n_assoc = len(self.__associations.keys())
        rel = HypergraphRelation(self.timestamp, n_assoc, guid, suid, __lbl, _val, self, v, d)
        self.__associations[guid] = rel
        # Increment relation number
        match d:
            case EnumRelationDirection.IN:
                self.__cnt_in_relations += 1
                # Increment degree (out)
                if isinstance(v, IComposable):
                    v.inc_degree_out()
            case EnumRelationDirection.OUT:
                self.__cnt_out_relations += 1
                # Increment degree (in)
                if isinstance(v, IComposable):
                    v.inc_degree_in()
            case EnumRelationDirection.UNDEFINED:
                self.__cnt_out_relations += 1
                self.__cnt_in_relations += 1
                # Increment degree (both in and out)
                if isinstance(v, IComposable):
                    v.inc_degree_out()
                    v.inc_degree_in()

    def unassociate_vertex(self, v: HyperVertex):
        # TODO: unnassociation
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to remove incompatible element from graph")

    def associate_edge(self, r: typing.Tuple[typing.Any, EnumRelationDirection, float|typing.Iterable]):
        e, d, v = r
        if not isinstance(e, HyperEdge):
            raise InvalidHypergraphElementException("Unable to associate edge with incompatible element")
        # TODO: finish

    def element_in_edge(self, v: HypergraphElement) -> bool:
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to check containment of incompatible element")
        return True

    def all_relations(self) -> typing.Generator[HypergraphRelation, None, None]:
        for x in self.__associations.values():
            yield x
        for x in self.__relations.values():
            yield x

    def out_relations(self) -> typing.Generator[HypergraphRelation, None, None]:
        for x in filter(lambda relx: relx.is_out(), self.all_relations()):
            yield x

    def in_relations(self) -> typing.Generator[HypergraphRelation, None, None]:
        for x in filter(lambda relx: relx.is_in(), self.all_relations()):
            yield x

    def out_vertices(self):
        return map(lambda x: x.target, self.out_relations())

    def in_vertices(self):
        return map(lambda x: x.target, self.in_relations())

    def __iter__(self):
        return self.all_relations()

    # Overload operations

    def __iadd__(self, other):
        self.associate_vertex(other)
        return self

    def __isub__(self, other):
        self.unassociate_vertex(other)
        return self

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._named_attr
        elif isinstance(item, HypergraphElement):
            return self.element_in_edge(item)

    def __len__(self):
        return len(self.__relations.keys()) + len(self.__associations.keys())

    # Count properties

    @property
    def cnt_in_relations(self):
        return self.__cnt_in_relations

    @property
    def cnt_out_relations(self):
        return self.__cnt_out_relations

    def permutation_tuples(self):
        for x in self.in_relations():
            for y in self.out_relations():
                yield x.target, y.target, x.value, y.value

    def update_permutation_tuples(self):
        for t in self.permutation_tuples():
            self._permutation_tuples.append(t)

    @property
    def element_permutation(self):
        return self._permutation_tuples

    @property
    def directed_relation_permutation(self):
        for x in self.in_relations():
            for y in self.out_relations():
                yield x, y

    def directed_relation_permutation_with_condition(self, f: typing.Callable[[typing.Any], bool]):
        for x in self.in_relations():
            for y in self.out_relations():
                if f(x) and f(y):
                    yield x, y

    def sub_edges(self, depth=None):
        for x in self.get_children(lambda x: isinstance(x, HyperEdge), depth):
            yield x

    @property
    def adjacency_tensor(self):
        return self._adj

    @adjacency_tensor.setter
    def adjacency_tensor(self, adj):
        self._adj = adj

    def __hash__(self):
        return int.from_bytes(self.guid, "big")
