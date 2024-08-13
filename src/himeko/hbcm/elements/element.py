import abc
import typing
from collections import deque

from himeko.hbcm.exceptions.basic_exceptions import InvalidParentException


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



class HypergraphMetaElement(abc.ABC):

    def __init__(self, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        """

        :param timestamp: timestamp of creation
        :param guid: GUID of element (most likely a hash) on creation must be unique
        :param serial: serial number in certain domain (e.g. when inserted into an edge or as part of a vertex)
        """
        self.__timestamp = timestamp
        self.__guid = guid
        self.__serial = serial
        if not (parent is None or isinstance(parent, HypergraphMetaElement)):
            raise InvalidParentException("Invalid parent element to hypergraph element")
        self.__parent = parent
        self.__suid = suid
        self.__label = label
        # Template
        self._stereotype = StereotypeDefinition()

    @property
    def stereotype(self):
        return self._stereotype

    @stereotype.setter
    def stereotype(self, v):
        self._stereotype += v

    def add_stereotype(self, v):
        self._stereotype += v



    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def guid(self):
        return self.__guid

    @property
    def serial(self):
        return self.__serial

    @property
    def suid(self):
        return self.__suid

    @property
    def parent(self):
        return self.__parent

    @property
    def label(self):
        return self.__label


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
        # Indexing
        self._index_named_elements: typing.Dict[str, HypergraphElement] = {}
        # Usages
        self._usages: typing.Dict = {}

    @property
    def name(self):
        return self.__name

    def __setitem__(self, key: str, value):
        if isinstance(key, str):
            self._named_attr[key] = value

    def __getitem__(self, item):
        if isinstance(item, str):
            if item in self._named_attr:
                return self._named_attr[item]
            else:
                raise KeyError
        raise KeyError

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

