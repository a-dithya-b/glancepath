from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum


class NodeKind(StrEnum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"


class EdgeKind(StrEnum):
    CONTAINS = "contains"
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"


@dataclass(frozen=True, slots=True)
class Node:
    id: str
    name: str
    kind: NodeKind
    file: str
    start_line: int
    end_line: int
    module: str
    parent_id: str | None = None


@dataclass(frozen=True, slots=True)
class Edge:
    source: str
    target: str
    kind: EdgeKind
    file: str | None = None
    line: int | None = None


@dataclass(frozen=True, slots=True)
class UnresolvedCall:
    source: str
    expression: str
    file: str
    line: int


@dataclass(slots=True)
class CodeGraph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    unresolved_calls: list[UnresolvedCall] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def add_unresolved_call(self, call: UnresolvedCall) -> None:
        self.unresolved_calls.append(call)

    def to_dict(self) -> dict[str, object]:
        return {
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [asdict(edge) for edge in self.edges],
            "unresolved_calls": [asdict(call) for call in self.unresolved_calls],
        }
