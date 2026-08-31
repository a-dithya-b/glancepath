from __future__ import annotations

import ast
from pathlib import Path

from glancepath.graph.model import CodeGraph, Edge, EdgeKind, Node, NodeKind


class PythonScanner(ast.NodeVisitor):
    def __init__(self, *, root: Path, file: Path, module: str, graph: CodeGraph) -> None:
        self.root = root
        self.file = file
        self.module = module
        self.graph = graph
        self.parents: list[str] = [module]

    @property
    def relative_file(self) -> str:
        return self.file.relative_to(self.root).as_posix()

    def _symbol_id(self, name: str) -> str:
        parent = self.parents[-1]
        if parent == self.module:
            return f"{self.module}:{name}"
        return f"{parent}.{name}"

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        symbol_id = self._symbol_id(node.name)
        parent_id = self.parents[-1]
        self.graph.add_node(
            Node(
                id=symbol_id,
                name=node.name,
                kind=NodeKind.CLASS,
                file=self.relative_file,
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                module=self.module,
                parent_id=parent_id,
            )
        )
        self.graph.add_edge(Edge(parent_id, symbol_id, EdgeKind.CONTAINS, self.relative_file, node.lineno))
        self.parents.append(symbol_id)
        self.generic_visit(node)
        self.parents.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        parent_id = self.parents[-1]
        kind = NodeKind.METHOD if parent_id != self.module else NodeKind.FUNCTION
        symbol_id = self._symbol_id(node.name)
        self.graph.add_node(
            Node(
                id=symbol_id,
                name=node.name,
                kind=kind,
                file=self.relative_file,
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                module=self.module,
                parent_id=parent_id,
            )
        )
        self.graph.add_edge(Edge(parent_id, symbol_id, EdgeKind.CONTAINS, self.relative_file, node.lineno))
        self.parents.append(symbol_id)
        self.generic_visit(node)
        self.parents.pop()


def module_name(root: Path, file: Path) -> str:
    relative = file.relative_to(root).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) or root.name


def scan_repository(path: str | Path) -> CodeGraph:
    root = Path(path).resolve()
    graph = CodeGraph()

    for file in sorted(root.rglob("*.py")):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in file.parts):
            continue

        module = module_name(root, file)
        relative_file = file.relative_to(root).as_posix()
        module_node = Node(
            id=module,
            name=module,
            kind=NodeKind.MODULE,
            file=relative_file,
            start_line=1,
            end_line=max(1, len(file.read_text(encoding="utf-8").splitlines())),
            module=module,
        )
        graph.add_node(module_node)

        source = file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file))
        PythonScanner(root=root, file=file, module=module, graph=graph).visit(tree)

    return graph
