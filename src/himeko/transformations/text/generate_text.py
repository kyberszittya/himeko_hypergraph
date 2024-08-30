from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.interfaces.base_interfaces import IComposable


def generate_signature_text(root: HypergraphElement):
    sig = f"{root.name}"
    if len(root.stereotype) > 0:
        sig += ": "
        for st in root.stereotype:
            sig += f" -> {st.name}"
    return sig + " {\n"


def generate_text(root: HypergraphElement, indent=0):
    text = " " * indent + generate_signature_text(root)

    for c in root.get_children(lambda x: True, 1):
        if isinstance(c, IComposable) and isinstance(c, HypergraphElement):
            text += generate_text(c, indent + 2)
    text += indent * " " + "}\n"
    return text
