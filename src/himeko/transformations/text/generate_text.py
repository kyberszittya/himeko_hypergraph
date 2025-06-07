from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge, HyperArc
from himeko.hbcm.elements.element import HypergraphElement, common_ancestor
from himeko.hbcm.elements.interfaces.base_interfaces import IComposable
from himeko.hbcm.elements.vertex import HyperVertex

from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge


class CommonOperations(object):

    @staticmethod
    def get_reference_name(referer: HypergraphElement, reference: HypergraphElement):
        __ancestor = common_ancestor(referer, reference)
        __el = reference
        __res = []
        while True:
            if __el is None or __ancestor == __el:
                break
            __res.append(__el.name)
            __el = __el.parent

        return __res[::-1]

    @staticmethod
    def generate_reference_text(referer: HypergraphElement, reference: HypergraphElement):
        return '.'.join(CommonOperations.get_reference_name(referer, reference))


class MetaElementTextGenerator(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)

    def generate_meta_element(self, root: HyperVertex, indent_step=2):
        text = ""
        if isinstance(root, HyperVertex):
            if root.meta is not None:
                text += f"[ {root.meta.context_name}\n"
                for imp in root.meta.imports:
                    text += " " * indent_step + f"import \"{imp}\"\n"
                text += "]\n"
        return text

    def __call__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], HyperVertex) and isinstance(args[1], int):
            root, indent = args
            return self.generate_meta_element(root, indent)
        else:
            return ""


class ElementSignatureTextGenerator(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)

    def generate_signature_text(self, root: HypergraphElement):
        sig = ""
        if isinstance(root, HyperEdge):
            sig += "@"
        sig += f"{root.name}"
        if len(root.stereotype) > 0:
            sig += ":"
            for st in root.stereotype:
                sig += f" -> {CommonOperations.generate_reference_text(root, st)} "
        return sig + " {\n"

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], HypergraphElement):
            root, = args
            return self.generate_signature_text(root)
        else:
            raise ValueError("Invalid arguments")





class EdgeBodyTextGenerator(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)



    def generate_edge_body_text(self, edge: HyperEdge, indent=0):
        text = ""
        for r in edge.all_relations():
            text += " " * indent + self.generate_relation_text(edge, r) +"\n"
        return text

    def generate_relation_text(self, edge: HyperEdge, r: HyperArc):
        if r.value == 1.0:
            return f"{r.direction} {CommonOperations.generate_reference_text(edge, r.target)}, "
        else:
            return f"{r.value} {r.direction} {CommonOperations.generate_reference_text(edge, r.target)}, "


    def __call__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], HyperEdge) and isinstance(args[1], int):
            edge, indent = args
            return self.generate_edge_body_text(edge, indent)
        if len(args) == 1 and isinstance(args[0], HyperEdge) and "indent" in kwargs:
            edge = args[0]
            return self.generate_edge_body_text(edge, kwargs["indent"])
        else:
            raise ValueError("Invalid arguments")


class TextGenerator(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self.__meta_element_text_generator = MetaElementTextGenerator(
            "meta_element_text_generator", timestamp, serial, guid, suid,
            '/'.join([label, "meta_element_generator"]), parent)
        self.__generate_signature_text = ElementSignatureTextGenerator(
            "generate_signature_text", timestamp, serial, guid, suid,
            '/'.join([label, "signature_generator"]), parent)
        self.__edge_body_text_generator = EdgeBodyTextGenerator(
            "edge_body_text_generator", timestamp, serial, guid, suid,
            '/'.join([label, "edge_body_generator"]), parent)

    def generate_text(self, root: HypergraphElement, indent=0, indent_step=2):
        text = ""
        text += self.__meta_element_text_generator(root, indent_step)
        text += " " * indent + self.__generate_signature_text(root)
        if isinstance(root, HyperEdge):
            text += self.__edge_body_text_generator(root, indent=indent + indent_step)
            text = text[:-3]
            text += "\n"
        for c in root.get_children(lambda x: isinstance(x, HypergraphAttribute), 1):
            if isinstance(c, HypergraphAttribute):
                text += " " * (indent + indent_step) + f"{c.name} {c.value}\n"
        for c in root.get_children(lambda x: isinstance(x, IComposable), 1):
            if isinstance(c, IComposable) and isinstance(c, HypergraphElement):
                text += self.generate_text(c, indent + indent_step)
        text += indent * " " + "}\n"
        return text

    def __call__(self, *args, **kwargs):
        if (len(args) == 3 and isinstance(args[0], HypergraphElement)
                and isinstance(args[1], int)
                and isinstance(args[2], int)):
            root, indent, indent_step = args
            return self.generate_text(root, indent, indent_step)
        elif len(args) == 1 and isinstance(args[0], HypergraphElement):
            root, = args
            return self.generate_text(root)
        else:
            raise ValueError("Invalid arguments")





