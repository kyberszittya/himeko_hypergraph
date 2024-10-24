from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge, Hyperarc
from himeko.hbcm.elements.element import HypergraphElement, common_ancestor
from himeko.hbcm.elements.interfaces.base_interfaces import IComposable
from himeko.hbcm.elements.vertex import HyperVertex


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


def generate_reference_text(referer: HypergraphElement, reference: HypergraphElement):
    return '.'.join(get_reference_name(referer, reference))


def generate_signature_text(root: HypergraphElement):
    sig = ""
    if isinstance(root, HyperEdge):
        sig += "@"
    sig += f"{root.name}"
    if len(root.stereotype) > 0:
        sig += ":"
        for st in root.stereotype:
            sig += f" -> {generate_reference_text(root, st)} "
    return sig + " {\n"


def generate_relation_text(edge: HyperEdge, r: Hyperarc):
    if r.value == 1.0:
        return f"{r.direction} {generate_reference_text(edge, r.target)}, "
    else:
        return f"{r.value} {r.direction} {generate_reference_text(edge, r.target)}, "


def generate_edge_body_text(edge: HyperEdge, indent=0):
    text = ""
    for r in edge.all_relations():
        text += " " * indent + generate_relation_text(edge, r) +"\n"
    return text


def generate_meta_element(root: HyperVertex, indent_step=2):
    text = ""
    if isinstance(root, HyperVertex):
        if root.meta is not None:
            text += f"[ {root.meta.filename}\n"
            for imp in root.meta.imports:
                text += " " * indent_step + f"import \"{imp}\"\n"
            text += "]\n"
    return text


def generate_text(root: HypergraphElement, indent=0, indent_step=2):
    text = ""
    text += generate_meta_element(root, indent_step)
    text += " " * indent + generate_signature_text(root)
    if isinstance(root, HyperEdge):
        text += generate_edge_body_text(root, indent=indent + indent_step)
        text = text[:-3]
        text += "\n"
    for c in root.get_children(lambda x: isinstance(x, HypergraphAttribute), 1):
        if isinstance(c, HypergraphAttribute):
            text += " " * (indent + indent_step) + f"{c.name} {c.value}\n"
    for c in root.get_children(lambda x: isinstance(x, IComposable), 1):
        if isinstance(c, IComposable) and isinstance(c, HypergraphElement):
            text += generate_text(c, indent + indent_step)
    text += indent * " " + "}\n"
    return text
