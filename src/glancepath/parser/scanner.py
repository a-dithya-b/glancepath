from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from glancepath.graph.model import (
    CodeGraph,
    Edge,
    EdgeKind,
    Node,
    NodeKind,
    UnresolvedCall,
)


@dataclass(slots=True)
class ModuleContext:
    module: str
    file: Path
    source: str
    tree: ast.Module
    imported_names: dict[str, str] = field(default_factory=dict)
    imported_modules: dict[str, str] = field(default_factory=dict)


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


class ImportCollector(ast.NodeVisitor):
    def __init__(self, context: ModuleContext) -> None:
        self.context = context

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local_name = alias.asname or alias.name.split(".")[0]
            self.context.imported_modules[local_name] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None or node.level:
            return
        for alias in node.names:
            if alias.name == "*":
                continue
            local_name = alias.asname or alias.name
            self.context.imported_names[local_name] = f"{node.module}:{alias.name}"


class CallResolver(ast.NodeVisitor):
    def __init__(self, *, root: Path, context: ModuleContext, graph: CodeGraph) -> None:
        self.root = root
        self.context = context
        self.graph = graph
        self.parents: list[str] = [context.module]

    @property
    def relative_file(self) -> str:
        return self.context.file.relative_to(self.root).as_posix()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        symbol_id = self._child_symbol_id(node.name)
        self.parents.append(symbol_id)
        self.generic_visit(node)
        self.parents.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        symbol_id = self._child_symbol_id(node.name)
        self.parents.append(symbol_id)
        self.generic_visit(node)
        self.parents.pop()

    def _child_symbol_id(self, name: str) -> str:
        parent = self.parents[-1]
        if parent == self.context.module:
            return f"{self.context.module}:{name}"
        return f"{parent}.{name}"

    def visit_Call(self, node: ast.Call) -> None:
        source = self.parents[-1]
        if source == self.context.module:
            self.generic_visit(node)
            return

        target = self._resolve_call(node.func, source)
        if target is not None:
            self.graph.add_edge(Edge(source, target, EdgeKind.CALLS, self.relative_file, node.lineno))
        else:
            expression = ast.unparse(node.func) if hasattr(ast, "unparse") else "<call>"
            self.graph.add_unresolved_call(
                UnresolvedCall(source=source, expression=expression, file=self.relative_file, line=node.lineno)
            )

        self.generic_visit(node)

    def _resolve_call(self, func: ast.expr, source: str) -> str | None:
        if isinstance(func, ast.Name):
            imported = self.context.imported_names.get(func.id)
            if imported and imported in self.graph.nodes:
                return imported

            same_module = f"{self.context.module}:{func.id}"
            if same_module in self.graph.nodes:
                return same_module
            return None

        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name) and func.value.id == "self":
                class_id = self.graph.nodes.get(source).parent_id if source in self.graph.nodes else None
                if class_id:
                    method_id = f"{class_id}.{func.attr}"
                    if method_id in self.graph.nodes:
                        return method_id
                return None

            if isinstance(func.value, ast.Name):
                module = self.context.imported_modules.get(func.value.id)
                if module:
                    target = f"{module}:{func.attr}"
                    if target in self.graph.nodes:
                        return target
            return None

        return None


def module_name(root: Path, file: Path) -> str:
    relative = file.relative_to(root).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) or root.name


def scan_repository(path: str | Path) -> CodeGraph:
    root = Path(path).resolve()
    graph = CodeGraph()
    contexts: list[ModuleContext] = []

    for file in sorted(root.rglob("*.py")):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in file.parts):
            continue

        module = module_name(root, file)
        relative_file = file.relative_to(root).as_posix()
        source = file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file))

        module_node = Node(
            id=module,
            name=module,
            kind=NodeKind.MODULE,
            file=relative_file,
            start_line=1,
            end_line=max(1, len(source.splitlines())),
            module=module,
        )
        graph.add_node(module_node)
        PythonScanner(root=root, file=file, module=module, graph=graph).visit(tree)
        contexts.append(ModuleContext(module=module, file=file, source=source, tree=tree))

    for context in contexts:
        ImportCollector(context).visit(context.tree)
        CallResolver(root=root, context=context, graph=graph).visit(context.tree)

    return graph
