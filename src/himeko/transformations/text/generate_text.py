from himeko.hbcm.elements.element import HypergraphElement, common_ancestor
from himeko.hbcm.elements.interfaces.base_interfaces import IComposable


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


def generate_signature_text(root: HypergraphElement):
    sig = f"{root.name}"
    if len(root.stereotype) > 0:
        sig += ": "
        for st in root.stereotype:
            sig += f" -> {'.'.join(get_reference_name(root, st))}"
    return sig + " {\n"


def generate_text(root: HypergraphElement, indent=0):
    text = " " * indent + generate_signature_text(root)

    for c in root.get_children(lambda x: True, 1):
        if isinstance(c, IComposable) and isinstance(c, HypergraphElement):
            text += generate_text(c, indent + 2)
    text += indent * " " + "}\n"
    return text
