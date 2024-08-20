import logging
import typing

from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.interfaces.base_interfaces import IComposable
from himeko.hbcm.exceptions.basic_exceptions import InvalidParentException


class HyperVertex(HypergraphElement, IComposable):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None):
        """

        :param name: name of vertex
        :param timestamp: timestamp of creation
        :param serial: serial number in a certain domain
        :param guid: unique GUID of element
        :param suid: UID derived from domain inception
        """
        if not (isinstance(parent, HyperVertex) or parent is None):
            raise InvalidParentException("Parent element invalid")
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        # Add current element to parent
        if parent is not None:
            parent.add_element(self)
        # Setup degree attributes
        self._degree_in = 0
        self._degree_out = 0
        # Adding logger element (ya rly)
        self._logger = logging.getLogger(f"{self.label}")


    @property
    def attribute_names(self):
        return [c for c in self._named_attr.keys()]

    @property
    def degree_in(self):
        return self._degree_in

    @property
    def degree_out(self):
        return self._degree_out

    def inc_degree_in(self):
        self._degree_in += 1

    def inc_degree_out(self):
        self._degree_out += 1

    def dec_degree_in(self):
        self._degree_in -= 1

    def dec_degree_out(self):
        self._degree_out -= 1

    @property
    def degree(self):
        return self._degree_in + self._degree_out

    def __iadd__(self, other):
        if isinstance(other, typing.Iterable):
            for o in other:
                self.add_element(o)
        else:
            self.add_element(other)
        return self

    def __isub__(self, other):
        self.remove_element(other)
        return self

    def __imul__(self, other):
        """
        Update elements
        :param other:
        :return:
        """
        if isinstance(other, typing.Iterable):
            for o in other:
                self.update_element(o)
        else:
            self.update_element(other)
        return self

    def __len__(self):
        return len(self._elements.values())

    def __hash__(self):
        return int.from_bytes(self.guid, "big")

    def get_children_nodes(self, condition: typing.Callable[[HypergraphElement], bool], depth: typing.Optional[int] = 1):
        return self.get_subelements(lambda x:
                                    x is not self and
                                    isinstance(x, HyperVertex) and
                                    condition(x), depth)
