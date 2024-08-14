import logging
import typing

from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.exceptions.basic_exceptions import InvalidParentException



class HyperVertex(HypergraphElement):

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
        # Adding logger element (ya rly)
        self._logger = logging.getLogger(f"{self.label}")


    @property
    def attribute_names(self):
        return [c for c in self._named_attr.keys()]



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




