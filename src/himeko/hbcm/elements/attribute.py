import typing

from himeko.hbcm.elements.element import HypergraphElement, HypergraphMetaElement


class HypergraphAttribute(HypergraphElement):

    def __init__(self, name: str, value: typing.Any, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HypergraphMetaElement] = None) -> None:
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self.__value = value

    @property
    def value(self):
        return self.__value
