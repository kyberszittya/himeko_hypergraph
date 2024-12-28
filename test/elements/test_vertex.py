import unittest

from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements, create_default_vertex_guid


class TestVertex(unittest.TestCase):

    def test_vertex_creation(self):
        v0 = FactoryHypergraphElements.create_vertex_default("vertex0", 0, None)
        assert v0.label == "vertex0.0"
        assert v0.guid == create_default_vertex_guid(v0.name, v0.timestamp, None)
        assert v0.suid != v0.guid
        assert v0.name == "vertex0"
        assert v0.serial == 0
        assert v0.timestamp == 0


    def test_vertex_creation_compose2(self):
        vparent = FactoryHypergraphElements.create_vertex_default("vertexparent", 0, None)
        v0 = FactoryHypergraphElements.create_vertex_default("v0", 0, vparent)
        v1 = FactoryHypergraphElements.create_vertex_default("v1", 0, vparent)
        assert v0.serial == 0
        assert v1.serial == 1
        assert v0.parent is vparent
        assert v1.parent is vparent
        assert v0.label == "vertexparent.0//v0.0"
        assert v1.label == "vertexparent.0//v1.0"

