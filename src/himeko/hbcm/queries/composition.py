import typing

from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.queries.definitions import QueryOperator, QueryInvalidOperands


class QueryIsStereotypeOperation(QueryOperator):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes,
                 suid: bytes, label: str,
                 parent: typing.Optional[HypergraphElement] = None,
                 stereotype: typing.Optional[HypergraphElement] = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        if stereotype is not None:
            self["stereotype"] = stereotype

    def operate(self, *args, **kwargs) -> typing.List[bool]:
        if len(args) < 2:
            if "stereotype" not in self._named_attr:
                raise QueryInvalidOperands(
                    "At least two operands are required for this operation or the definition of stereotype field")
            else:
                stereotype: HypergraphElement = self["stereotype"]
                # Get operands
                operands = args
        else:
            if "stereotype" in self:
                stereotype: HypergraphElement = self["stereotype"]
                # Get operands
                operands = args
            else:
                # Operator precedence: stereotype and other operands
                stereotype: HypergraphElement = args[0]
                # Get operands
                operands = args[1:]
        # Check if stereotype is defined
        if not isinstance(args[0], HypergraphElement):
            raise QueryInvalidOperands("First operand must be a graph element")
        # Check if depth is defined as an integer in kwargs
        if "depth" not in kwargs:
            depth = None
        else:
            depth = kwargs["depth"]
        # Check is all args are Hypergraph elements
        for arg in args:
            if not isinstance(arg, HypergraphElement):
                raise QueryInvalidOperands("All operands must be graph elements")
        # Get results in each operand
        result = []
        for h in operands:
            h: HypergraphElement
            result.extend(
                list(h.get_children(lambda x: stereotype.name in x.stereotype.nameset, depth))
            )
        return result
