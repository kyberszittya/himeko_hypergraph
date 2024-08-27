import os
import math
import typing
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader

from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation


@dataclass
class MxwNode(object):
    name: str
    position: typing.Optional[list]
    orientation: typing.Optional[list]
    scale: typing.Optional[list]
    mesh: typing.Optional[typing.Dict]
    children: typing.Dict




class TransformationMxw(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str,
                 parent: HypergraphElement = None, mxw_meta=None, units=None):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)
        self._named_attr["mxw_meta"] = mxw_meta
        self._named_attr["units"] = units

    @staticmethod
    def __orientation_order(euler, units):
        if units.value["axis"].value.lower() == "xyz":
            return euler[2], euler[0], euler[1]
        elif units.value["axis"].value.lower() == "xzy":
            return euler[1], euler[2], euler[0]
        return euler[0], euler[1], euler[2]

    def __convert_euler_to_quaternion(self, euler):

        if self["units"] is not None:
            if self["units"].value["angle"].value == "degree":
                print(self.__orientation_order([math.radians(x) for x in euler], self["units"]))
                x, y, z = self.__orientation_order([math.radians(x) for x in euler], self["units"])
            elif self["units"].value["angle"].value == "radian":
                x, y, z = self.__orientation_order(euler, self["units"])
            else:
                x, y, z = euler
        else: # default
            x, y, z = euler
        x = x * 0.5
        y = y * 0.5
        z = z * 0.5
        cr = math.cos(x)
        sr = math.sin(x)
        cp = math.cos(y)
        sp = math.sin(y)
        cy = math.cos(z)
        sy = math.sin(z)
        q = [0, 0, 0, 0]
        q[0] = cy * cp * cr + sy * sp * sr
        q[1] = sr * cp * cy - cr * sp * sy
        q[2] = cr * sp * cy + sr * cp * sy
        q[3] = cr * cp * sy - sr * sp * cy
        return q

    @staticmethod
    def __position_axis_order(position, units):
        if units.value["axis"].value.lower() == "xyz":
            return position[0], position[2], position[1]
        elif units.value["axis"].value.lower() == "xzy":
            return position[0], position[1], position[2]
        return position[1], position[0], position

    def __create_mxw_node(self, r: HypergraphElement):
        nmxw = MxwNode(r.name, None, None, None, None, {})
        if "position" in r:
            nmxw.position = self.__position_axis_order(r["position"].value, self["units"])
        if "orientation" in r:
            nmxw.orientation = self.__convert_euler_to_quaternion(r["orientation"].value)
        if "scale" in r:
            nmxw.scale = r["scale"].value
        if "mesh" in r:
            nmxw.mesh = {}
            nmxw.mesh["url"] = r["mesh"]["url"].value
            if "scale" in r["mesh"]:
                nmxw.mesh["scale"] = r["mesh"]["scale"].value
        return nmxw

    def __mxw_node_process(self, node: MxwNode, n: HypergraphElement):
        if n.count_composite_elements != 0:
            res_node = self.op_mxw_node(n, depth=1)
            for r in res_node:
                nmxw = self.__create_mxw_node(r)
                node.children[r.name] = nmxw
                self.__mxw_node_process(nmxw, r)

    def operate(self, *args, **kwargs):
        if self._named_attr["mxw_meta"] is None:
            raise ValueError("MaxWhere kinematics meta not set")
        root = args[0]
        mxw_node = self["mxw_meta"]["elements"]["mxw_node"]
        self.op_mxw_node = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "mxw_node_stereotype", 0,
            stereotype=mxw_node
        )
        res_node = self.op_mxw_node(root, depth=1)
        tree = None
        for r in res_node:
            if tree is None:
                tree = self.__create_mxw_node(r)
            self.__mxw_node_process(tree, r)
        print(os.getcwd())
        template_path = (os.path.join(os.path.dirname(__file__), 'templates'))

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader(template_path))

        template = env.get_template('template.jinja')
        # define context to substitute in the template
        context = {
            'tree': tree
        }

        # Render template
        rendered_html = template.render(context)
        return rendered_html


