import abc
import typing
from himeko_hypergraph.src.elements.edge import ExecutableHyperEdge, EnumRelationDirection
from himeko_hypergraph.src.elements.vertex import ExecutableHyperVertex, HyperVertex

from collections import deque


class MessageQueueVertex(ExecutableHyperVertex):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None, transform_func: typing.Optional[typing.Callable] = None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self._message_queue = deque()
        self._cnt_msg = 0
        if transform_func is None:
            self._transform_func = lambda x: x
        else:
            self._transform_func = transform_func

    @abc.abstractmethod
    def _push_operation(self, *args, **kwargs):
        raise NotImplementedError

    def push(self, *args, **kwargs):
        _msg = self._push_operation(*args, **kwargs)
        self._cnt_msg += 1
        self._message_queue.append(_msg)

    def operate(self):
        if self._cnt_msg > 0:
            _msg = self._message_queue.popleft()
            self._cnt_msg -= 1
            return self._transform_func(_msg)
        return None

    @property
    def cnt_msg(self):
        return self._cnt_msg


class FlowVertex(MessageQueueVertex):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional = None, transform_func: typing.Optional[typing.Callable] = None,
                 flow_direction: EnumRelationDirection = EnumRelationDirection.UNDEFINED):
        super().__init__(name, timestamp, serial, guid, suid, label, parent, transform_func)
        self._msg_queue = None
        self.__flow_direction = flow_direction

    @abc.abstractmethod
    def _input_operation(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _output_operation(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _bidirectional_operation(self, *args, **kwargs):
        raise NotImplementedError

    def _push_operation(self, *args, **kwargs):
        match self.__flow_direction:
            case EnumRelationDirection.UNDEFINED:
                return self._bidirectional_operation(*args, **kwargs)
            case EnumRelationDirection.IN:
                return self._input_operation(*args, **kwargs)
            case EnumRelationDirection.OUT:
                return self._output_operation(*args, **kwargs)

    @property
    def flow_direction(self):
        return self.__flow_direction


class SequentialExecutionEdge(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HyperVertex],
                 sequence: typing.Optional[typing.List[ExecutableHyperEdge]] = None) -> None:
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        if sequence is not None:
            self.__operation_sequence = sequence
        else:
            self.__operation_sequence = []

    def push_input_message(self, msg):
        for v in filter(lambda x: isinstance(x, MessageQueueVertex), self.in_vertices()):
            v: MessageQueueVertex
            v.push(msg)

    def operate(self):
        outputs = []
        for v in filter(lambda x: isinstance(x, MessageQueueVertex), self.in_vertices()):
            outputs.append(v())
        for op in self.__operation_sequence:
            outputs = op(outputs)
        for v in filter(lambda x: isinstance(x, MessageQueueVertex), self.out_vertices()):
            v: MessageQueueVertex
            if outputs is not None:
                for o in outputs:
                    v.push(o)


class MessageQueueEdge(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: typing.Optional[HyperVertex], transform_func: typing.Optional[typing.Callable] = None) -> None:
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        if transform_func is None:
            self.__transform_func = lambda x,y: x
        else:
            self.__transform_func = transform_func


    def operate(self):
        outputs = []
        out_mq_vertices = list(filter(lambda x: isinstance(x, MessageQueueVertex), self.out_vertices()))
        for v in filter(lambda x: isinstance(x, MessageQueueVertex), self.in_vertices()):
            token = self.__transform_func(v(), self._named_attr)
            for _ in range(len(out_mq_vertices)):
                outputs.append(token)
        for v in out_mq_vertices:
            v: MessageQueueVertex
            for o in outputs:
                v.push(o)
