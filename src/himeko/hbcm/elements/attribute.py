import typing

from himeko.hbcm.elements.element import HypergraphElement, HypergraphMetaElement
from himeko.hbcm.elements.vertex import HyperVertex


class HypergraphAttribute(HypergraphElement):

    def __init__(self, name: str, value: typing.Any, type: str,
                 timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphMetaElement] = None) -> None:
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        # Parent
        if parent is not None:
            parent: HyperVertex
            parent.add_element(self)
        self.__value = value
        self.__type = type

    @property
    def value(self):
        return self.__value

    @property
    def type(self):
        return self.__type
