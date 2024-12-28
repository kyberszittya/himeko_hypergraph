import abc
import typing
from collections import deque
from dataclasses import dataclass

from himeko.hbcm.elements.interfaces.base_interfaces import IComposable
from himeko.hbcm.exceptions.basic_exceptions import (InvalidHypergraphElementException,
                                                     InvalidParentException, ElementSelfParentException)
from himeko.hbcm.graph.prufer_sequence import generate_naive_prufer


class StereotypeDefinition(abc.ABC):

    def __init__(self):
        self._stereotype = set()
        self._index_named_elements = {}

    def __add__(self, other):
        self._stereotype.add(other)
        # Add index
        self._index_named_elements[other.name] = other
        return self

    def __iter__(self):
        return iter(self._stereotype)

    def __len__(self):
        return len(self._stereotype)

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self.nameset
        return item in self.__stereotype_fringe()

    def __stereotype_fringe(self):
        res = set()
        fringe = deque()
        fringe.extend(self._stereotype)
        while len(fringe) != 0:
            __e = fringe.pop()
            for x in __e.stereotype.leaf_stereotypes:
                if x.name not in res:
                    fringe.appendleft(x)
            res.add(__e)
        return res

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._index_named_elements[item]
        if isinstance(item, int):
            return list(self._stereotype)[item]
        return None

    def __sub__(self, other):
        self._stereotype.remove(other)
        # Remove index
        self._index_named_elements.pop(other.name)
        return self

    @property
    def nameset(self):
        res = set()
        fringe = deque()
        fringe.extend(self._stereotype)
        while len(fringe) != 0:
            __e = fringe.pop()
            for x in __e.stereotype.leaf_stereotypes:
                if x.name not in res:
                    fringe.appendleft(x)
            res.add(__e.name)
        return res

    @property
    def leaf_stereotypes(self):
        return self._stereotype

    @property
    def elements(self):
        return self._stereotype


@dataclass
class InformationIdentityFragment:
    timestamp: int
    serial: int
    guid: bytes
    suid: bytes
    label: str


class HypergraphMetaElement(abc.ABC):

    def __init__(self, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        """

        :param timestamp: timestamp of creation
        :param guid: GUID of element (most likely a hash) on creation must be unique
        :param serial: serial number in certain domain (e.g. when inserted into an edge or as part of a vertex)
        """
        self.__fragment = InformationIdentityFragment(timestamp, serial, guid, suid, label)

        if not (parent is None or isinstance(parent, HypergraphMetaElement)):
            raise InvalidParentException("Invalid parent element to hypergraph element")
        self._parent = parent
        # Template
        self._stereotype = StereotypeDefinition()

    @property
    def stereotype(self) -> StereotypeDefinition:
        return self._stereotype

    @stereotype.setter
    def stereotype(self, v: StereotypeDefinition):
        self._stereotype += v

    def add_stereotype(self, v):
        self._stereotype += v

    @property
    def timestamp(self):
        return self.__fragment.timestamp

    @property
    def guid(self):
        return self.__fragment.guid

    @property
    def serial(self):
        return self.__fragment.serial

    @property
    def suid(self):
        return self.__fragment.suid

    """
    Parent in the compositional tree.
    """
    @property
    def parent(self):
        return self._parent

    @property
    def label(self):
        return self.__fragment.label


class HypergraphElement(HypergraphMetaElement):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphMetaElement] = None) -> None:
        """

        :param name: Name of element
        :param timestamp: timestamp of creation
        :param serial: serial number in certain domain
        :param guid: GUID of element (most likely a hash)
        :param suid: UID derived from domain inception
        """
        super().__init__(timestamp, serial, guid, suid, label, parent)
        self.__name = name
        # Attributes
        self._named_attr: typing.Dict[str, typing.Any] = {}
        # Setup elements
        self._elements: typing.Dict[bytes, HypergraphElement] = {}
        # Composite graph elements (vertices and edges) count
        self._composite_count = 0
        # Indexing
        self._index_named_elements: typing.Dict[str, HypergraphElement] = {}
        # Usages
        self._usages: typing.Dict = {}
        # Element sequence
        self._element_sequence = None
        self._element_permutation = {}
        self._permutation_element = {}
        self._prufer_code = None
        self._node_map = {}

    @property
    def name(self):
        return self.__name

    def __lt__(self, other):
        return self.guid < other.guid

    def __setitem__(self, key: str, value):
        if isinstance(key, str):
            self._named_attr[key] = value

    def __getitem__(self, item):
        if isinstance(item, str):
            if item in self._named_attr:
                return self._named_attr[item]
            else:
                for s in self.stereotype.elements:
                    if item in s:
                        return s[item]
                raise KeyError
        raise KeyError

    def __generate_permuations(self):
        self._prufer_code, self._element_sequence, self._node_map = generate_naive_prufer(self)
        self._element_sequence.append(self)
        for i, s in enumerate(self._element_sequence):
            self._element_permutation[s] = i
            self._permutation_element[i] = s

    @property
    def prufer_code(self):
        if self.__element_count_changed():
            self.__generate_permuations()
        return self._prufer_code

    def __element_count_changed(self) -> bool:
        """
        Check if element sequence have been changed by comparing length of the element sequence
        to the number of composite elements
        Also brevity check for none element sequence
        :return:
        """
        if self._element_sequence is None or (self.count_composite_elements != len(self._element_sequence)):
            return True
        return False

    @property
    def permutation_sequence(self):
        if self.__element_count_changed():
            self.__generate_permuations()
        return self._element_sequence

    @property
    def children_permutation_sequence(self):
        if self.__element_count_changed():
            self.__generate_permuations()
        return self._element_sequence[:-1]

    @property
    def element_permutation(self):
        if self.__element_count_changed():
            self.__generate_permuations()
        return self._element_permutation

    @property
    def permutation_element(self):
        if self.__element_count_changed():
            self.__generate_permuations()
        return self._permutation_element

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._named_attr
        return False

    def __fringe_append(self, fringe, __e, d):
        for _, ch in __e._elements.items():
            fringe.appendleft((ch, d + 1))

    def __init_fringe(self, include_self: bool):
        visited = set()
        fringe = deque()
        if include_self:
            fringe.append((self, 0))
        else:
            self.__fringe_append(fringe, self, 0)
        return visited, fringe

    def get_subelements(self,
                        condition: typing.Callable[[typing.Any], bool],
                        depth: typing.Optional[int] = None, include_self=False):
        visited, fringe = self.__init_fringe(include_self)
        __res = []
        if depth is None:
            bound_condition = lambda x: True
        else:
            bound_condition = lambda x: d <= depth
        while len(fringe) != 0:
            __e, d = fringe.pop()
            if __e not in visited and bound_condition(d):
                visited.add(__e)
                if condition(__e):
                    __res.append(__e)
                    yield __e
                if isinstance(__e, HypergraphElement):
                    self.__fringe_append(fringe, __e, d)
        return __res

    def add_element(self, _v):
        v: HypergraphElement = _v
        # Ensure that the element is not itself
        if v is self:
            raise ElementSelfParentException("Parent element cannot be itself (composition loop)")
        # Check if element is a hypergraph element anyway
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to add incompatible element")
        self._elements[v.guid] = v
        self._index_named_elements[v.name] = v
        # Set element parent (if parent is not already self)
        if v.parent is not self:
            v._parent = self
        # Check attribute
        if isinstance(v, HypergraphElement):
            self._named_attr[v.name] = v
        # Update composite count
        if isinstance(v, IComposable):
            self._composite_count += 1

    def get_element(self, key: str):
        return self._index_named_elements[key]

    def remove_element(self, v: HypergraphMetaElement):
        if not isinstance(v, HypergraphElement):
            raise InvalidHypergraphElementException("Unable to remove incompatible element")
        self._elements.pop(v.guid)
        self._index_named_elements.pop(v.name)
        # Update composite count
        if isinstance(v, IComposable):
            self._composite_count -= 1

    def update_element(self, _v):
        v: HypergraphElement = _v
        if v.name not in self._index_named_elements:
            self.add_element(v)
        else:
            # Remove existing element
            __tmp = self._index_named_elements[v.name]
            self._elements.pop(__tmp.guid)
            self._index_named_elements[v.name] = v
            self._index_named_elements[v.guid] = v


    @property
    def count_composite_elements(self):
        return self._composite_count

    @property
    def leaf_elements(self):
        return self.get_children(lambda x: x.count_composite_elements == 0, None)

    def get_leaf_elements(self):
        return sorted(self.leaf_elements)

    def query_subelements(self, query: str):
        query_split = query.split(".")
        __next_element = self
        if query_split[0] != self.name:
            return None
        for q in query_split[1:]:
            __next_element = __next_element[q]
        return __next_element

    def get_children(self, condition: typing.Callable[[typing.Any], bool], depth: typing.Optional[int] = 1):
        return self.get_subelements(condition, depth)

    def get_all_children(self, condition: typing.Callable[[typing.Any], bool]):
        return self.get_subelements(condition, None)

    def get_parent(self):
        return self.parent

    def get_siblings(self, condition: typing.Callable[[typing.Any], bool]):
        if self.parent is None:
            return None
        return self.get_parent().get_children(condition, 1)


def common_ancestor(a: HypergraphElement, b: HypergraphElement):
    if a is b:
        return a
    elif a.parent is b:
        return b
    elif b.parent is a:
        return a
    elif a.parent is b.parent:
        return a.parent
    elif a.parent is None or b.parent is None:
        return None
    elif a.parent is not b.parent:
        return common_ancestor(a.parent, b.parent)
    else:
        return None
