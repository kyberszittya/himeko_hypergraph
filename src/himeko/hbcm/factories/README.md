# HBCM Elements

The `hbcm.elements` module provides a set of utilities and factories for creating and managing hypergraph elements, such as vertices, edges, and attributes. These elements are used to construct and manipulate hypergraphs in the context of the HBCM framework.

## Features

- **Vertex Creation**: Create vertices with unique identifiers, labels, and attributes.
- **Edge Creation**: Generate edges with globally unique identifiers and labels.
- **Attribute Management**: Add and modify attributes for vertices and edges.
- **Factory Classes**: Use factory methods to streamline the creation of hypergraph elements.
- **Clock Integration**: Support for timestamped element creation using an associated clock.

## Key Components

### Factory Classes

- **`FactoryHypergraphElements`**: Provides methods for creating default vertices, edges, and attributes.
- **`FactoryHypergraphElementsClock`**: Extends `FactoryHypergraphElements` to include timestamped creation using a clock.

### Functions

- **`create_default_vertex_guid`**: Generates a globally unique identifier (GUID) for a vertex.
- **`create_default_edge_guid`**: Generates a GUID for an edge.
- **`create_default_suid`**: Creates a shared unique identifier (SUID) by combining GUIDs.
- **`create_parent_based_serial`**: Computes a serial number based on the parent element.

## Usage

### Creating a Vertex

```python
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements

vertex = FactoryHypergraphElements.create_vertex_default("vertex_name", timestamp=123456789, parent=None)
print(vertex.label)  # Outputs: vertex_name.123456789
```
